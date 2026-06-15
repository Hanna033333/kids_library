import io
import time
import httpx
from PIL import Image
from core.config import THREADS_ACCESS_TOKEN, THREADS_USER_ID
from supabase_client import supabase

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
    
    # 1. 개별 이미지 컨테이너 병렬/순차 생성
    container_ids = []
    for idx, img_url in enumerate(image_urls):
        print(f"📦 [{idx+1}/{len(image_urls)}] 개별 이미지 컨테이너 생성 중...")
        item_id = await create_threads_item_container(img_url, THREADS_ACCESS_TOKEN, THREADS_USER_ID)
        container_ids.append(item_id)
        # API 과도한 호출 방지 위해 미세한 지연 추가
        time.sleep(1)
        
    # 2. 캐러셀 부모 컨테이너 생성
    print("📂 캐러셀 부모 컨테이너 조립 중...")
    parent_id = await create_threads_carousel_parent(container_ids, text, THREADS_ACCESS_TOKEN, THREADS_USER_ID)
    
    # 미디어가 완전히 처리될 수 있도록 업로드 완료 대기 (권장)
    print("⏳ Meta 미디어 서버 처리 대기 (5초)...")
    time.sleep(5)
    
    # 3. 최종 스레드 퍼블리시
    print("📣 스레드 피드에 최종 발행 중...")
    post_id = await publish_threads_container(parent_id, THREADS_ACCESS_TOKEN, THREADS_USER_ID)
    print(f"🎉 스레드 캐러셀 발행 성공! 포스트 ID: {post_id}")
    
    return post_id
