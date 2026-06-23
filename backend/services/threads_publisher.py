import io
import asyncio
import httpx
from PIL import Image
from core.config import THREADS_ACCESS_TOKEN, THREADS_USER_ID
from core.database import supabase

async def poll_container_status(container_id: str, access_token: str, max_retries: int = 20, interval: int = 5) -> str:
    """
    Threads 미디어 컨테이너가 FINISHED 상태가 될 때까지 폴링합니다.
    Threads API는 컨테이너가 FINISHED 상태가 되기 전에 carousel 조립을 시도하면 500 에러를 반환합니다.
    """
    url = f"https://graph.threads.net/v1.0/{container_id}"
    params = {
        "fields": "status,error_message",
        "access_token": access_token
    }

    for attempt in range(max_retries):
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=15)
            if response.status_code != 200:
                print(f"⚠️ 상태 조회 실패 (시도 {attempt+1}/{max_retries}): {response.text}")
                await asyncio.sleep(interval)
                continue

            data = response.json()
            status = data.get("status", "UNKNOWN")
            print(f"  ↳ 컨테이너 {container_id} 상태: {status}")

            if status == "FINISHED":
                return status
            elif status in ("ERROR", "EXPIRED"):
                error_msg = data.get("error_message", "알 수 없는 오류")
                raise RuntimeError(f"❌ 컨테이너 {container_id} 오류 상태: {status} - {error_msg}")

        await asyncio.sleep(interval)

    raise TimeoutError(f"❌ 컨테이너 {container_id}가 {max_retries * interval}초 내에 FINISHED 상태가 되지 않았습니다.")

async def upload_image_to_supabase(image: Image.Image, file_name: str) -> str:
    """
    Pillow 이미지를 Supabase Storage 'threads_assets' 버킷에 업로드하고 퍼블릭 URL을 획득합니다.
    """
    try:
        # 이미지를 바이트 배열로 변환
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        img_data = img_byte_arr.read()
        
        # 파일 업로드 (동일 이름 파일이 있을 경우 overwrite 방지를 위해 upsert=True 설정)
        bucket_name = "threads_assets"
        
        # storage 업로드 수행
        print(f"📤 Supabase Storage 업로드 중: {file_name}")
        supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=img_data,
            file_options={"content-type": "image/png", "x-upsert": "true"}
        )
        
        # 퍼블릭 URL 조회
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        print(f"🔗 업로드 성공! 퍼블릭 URL: {public_url}")
        return public_url
    except Exception as e:
        print(f"❌ Supabase Storage 업로드 실패: {e}")
        raise e

async def create_threads_item_container(image_url: str, access_token: str, user_id: str) -> str:
    """
    개별 카드뉴스 이미지에 대해 Threads 미디어 컨테이너(캐러셀 아이템)를 생성합니다.
    """
    url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    params = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "is_carousel_item": "true",
        "access_token": access_token
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"❌ 캐러셀 아이템 컨테이너 생성 실패: {response.text}")
            response.raise_for_status()
        
        data = response.json()
        return data["id"]

async def create_threads_carousel_parent(container_ids: list, text: str, access_token: str, user_id: str) -> str:
    """
    개별 이미지 컨테이너 ID 리스트를 엮어 메인 캐러셀 부모 컨테이너를 생성합니다.
    """
    url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    
    # children 파라미터는 쉼표로 연결된 문자열 형태여야 함
    children_str = ",".join(container_ids)
    
    params = {
        "media_type": "CAROUSEL",
        "text": text,
        "children": children_str,
        "access_token": access_token
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"❌ 캐러셀 부모 컨테이너 생성 실패: {response.text}")
            response.raise_for_status()
            
        data = response.json()
        return data["id"]

async def publish_threads_container(creation_id: str, access_token: str, user_id: str) -> str:
    """
    최종 구성된 부모 컨테이너를 스레드 피드에 발행합니다.
    """
    url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
    params = {
        "creation_id": creation_id,
        "access_token": access_token
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"❌ 최종 스레드 발행 실패: {response.text}")
            response.raise_for_status()
            
        data = response.json()
        return data["id"]

async def publish_carousel_to_threads(text: str, image_urls: list) -> str:
    """
    본문 글(text)과 이미지 URL 목록(image_urls)을 받아 스레드 캐러셀 포스트를 최종 발행합니다.
    """
    if not THREADS_ACCESS_TOKEN or not THREADS_USER_ID:
        raise ValueError("❌ 환경 변수에 THREADS_ACCESS_TOKEN 또는 THREADS_USER_ID가 설정되어 있지 않습니다.")
        
    if not image_urls:
        raise ValueError("❌ 발행할 이미지 URL 목록이 비어있습니다.")
        
    print(f"🚀 Threads 캐러셀 업로드 시작 (총 {len(image_urls)}개 이미지)")

    # 1. 개별 이미지 컨테이너 생성 → 각각 FINISHED 상태 확인
    container_ids = []
    for idx, img_url in enumerate(image_urls):
        print(f"📦 [{idx+1}/{len(image_urls)}] 개별 이미지 컨테이너 생성 중...")
        item_id = await create_threads_item_container(img_url, THREADS_ACCESS_TOKEN, THREADS_USER_ID)
        container_ids.append(item_id)
        await asyncio.sleep(1)

    # 모든 자식 컨테이너가 FINISHED 상태가 될 때까지 대기 (캐러셀 조립 전 필수)
    print("⏳ 자식 컨테이너 처리 완료 대기 중...")
    for cid in container_ids:
        await poll_container_status(cid, THREADS_ACCESS_TOKEN)

    # 2. 캐러셀 부모 컨테이너 생성
    print("📂 캐러셀 부모 컨테이너 조립 중...")
    parent_id = await create_threads_carousel_parent(container_ids, text, THREADS_ACCESS_TOKEN, THREADS_USER_ID)

    # 부모 컨테이너도 FINISHED 상태 확인 후 발행
    print("⏳ 부모 컨테이너 처리 완료 대기 중...")
    await poll_container_status(parent_id, THREADS_ACCESS_TOKEN)

    # 3. 최종 스레드 퍼블리시
    print("📣 스레드 피드에 최종 발행 중...")
    post_id = await publish_threads_container(parent_id, THREADS_ACCESS_TOKEN, THREADS_USER_ID)
    print(f"🎉 스레드 캐러셀 발행 성공! 포스트 ID: {post_id}")

    return post_id


async def publish_reply_to_threads(parent_post_id: str, reply_text: str) -> str:
    """
    부모 스레드 포스트 ID(parent_post_id)를 받아서 첫 번째 댓글(reply_text)을 자동으로 등록합니다.
    """
    if not THREADS_ACCESS_TOKEN or not THREADS_USER_ID:
        raise ValueError("❌ 환경 변수에 THREADS_ACCESS_TOKEN 또는 THREADS_USER_ID가 설정되어 있지 않습니다.")
        
    print(f"💬 Threads 댓글 작성 시작 (부모 포스트 ID: {parent_post_id})")
    
    # 1. 댓글 미디어 컨테이너 생성 (TEXT 타입)
    url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads"
    params = {
        "media_type": "TEXT",
        "text": reply_text,
        "reply_to_id": parent_post_id,
        "access_token": THREADS_ACCESS_TOKEN
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"❌ 댓글 컨테이너 생성 실패: {response.text}")
            response.raise_for_status()
            
        data = response.json()
        container_id = data["id"]
        
    # 2. 댓글 컨테이너 상태 폴링
    print(f"⏳ 댓글 컨테이너 {container_id} 처리 완료 대기 중...")
    await poll_container_status(container_id, THREADS_ACCESS_TOKEN)
    
    # 3. 댓글 최종 발행
    print("📣 스레드 댓글 최종 게시 중...")
    reply_post_id = await publish_threads_container(container_id, THREADS_ACCESS_TOKEN, THREADS_USER_ID)
    print(f"🎉 스레드 댓글 등록 성공! 댓글 포스트 ID: {reply_post_id}")
    
    return reply_post_id
