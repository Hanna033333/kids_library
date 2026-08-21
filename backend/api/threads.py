import os
import json
import uuid
import time
import urllib.parse
import datetime
import asyncio
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, Request, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx
from PIL import Image

from core.config import THREADS_ACCESS_TOKEN, THREADS_USER_ID
from core.taxonomy import get_weekly_curations, ALL_TAXONOMY
from core.database import supabase
from services.card_generator import generate_card_news
from services.threads_publisher import upload_image_to_supabase, publish_carousel_to_threads, publish_reply_to_threads
from services.telegram_notifier import send_threads_preview, send_threads_text_preview, send_telegram_message
from services.ai_content import generate_ai_threads_content, apply_feedback_with_gemini

router = APIRouter(prefix="/api/threads", tags=["threads"])

# 관리자 인증 토큰
THREADS_ADMIN_TOKEN = os.getenv("THREADS_ADMIN_TOKEN")

def ensure_threads_admin_token() -> str:
    """운영용 관리자 토큰이 반드시 설정되어 있어야 합니다."""
    if not THREADS_ADMIN_TOKEN:
        raise RuntimeError("THREADS_ADMIN_TOKEN is required for Threads admin routes")
    return THREADS_ADMIN_TOKEN

def sign_action(action: str, feed_id: int) -> str:
    """액션과 feed_id를 결합하여 보안 승인에 사용할 HMAC 서명을 생성합니다."""
    key = ensure_threads_admin_token().encode("utf-8")
    message = f"{action}:{feed_id}".encode("utf-8")
    import hmac
    import hashlib
    return hmac.new(key, message, hashlib.sha256).hexdigest()

def verify_action_signature(action: str, feed_id: int, signature: str) -> bool:
    """전달된 HMAC 서명을 검증합니다. (비교 시 타이밍 공격 방지를 위해 compare_digest 사용)"""
    import hmac
    expected = sign_action(action, feed_id)
    return hmac.compare_digest(expected, signature)

def get_backend_url() -> str:
    """안전한 백엔드 URL을 반환합니다. 임시 터널 주소(loca.lt, loca.it 등)는 상용 주소로 자동 교체합니다."""
    url = os.getenv("BACKEND_URL", "https://api.checkjari.com").strip().rstrip("/")
    if not url or "loca.lt" in url or "loca.it" in url or "localtunnel" in url:
        return "https://api.checkjari.com"
    if "localhost" in url or "127.0.0.1" in url:
        return url.replace("localhost", "lvh.me").replace("127.0.0.1", "lvh.me")
    return url

def _build_admin_url(base_url: str, path: str, feed_id: int, signature: str) -> str:
    """텔레그램 버튼에 사용할 관리자 승인 URL을 생성합니다."""
    parsed = urllib.parse.urlsplit(f"{base_url}{path}")
    query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    query["feed_id"] = str(feed_id)
    query["signature"] = signature
    return urllib.parse.urlunsplit((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        urllib.parse.urlencode(query),
        parsed.fragment,
    ))

def _require_admin_token(
    header_token: Optional[str] = None,
) -> str:
    """X-Admin-Token 헤더에서 관리자 토큰을 검증합니다."""
    expected = ensure_threads_admin_token()
    if header_token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid admin token")
    return expected

def is_scrap_bot(request: Request) -> bool:
    """요청 헤더의 User-Agent를 파악하여 메신저 스크랩/크롤링 봇인지 여부를 반환합니다."""
    ua = request.headers.get("user-agent", "").lower()
    bot_keywords = [
        "facebookexternalhit",  # 메타(스레드/페이스북/인스타)
        "kakaotalk-scrap",      # 카카오톡
        "twitterbot",           # 트위터
        "slackbot",             # 슬랙
        "telegrambot",          # 텔레그램
        "whatsapp",             # 왓츠앱
        "go-http-client"        # 기타 고랭 크롤러 등
    ]
    return any(k in ua for k in bot_keywords)

def get_bot_bypass_html(title: str, status: str) -> str:
    """스크랩 봇에 반환할 무해한 HTML 템플릿입니다. 비즈니스 로직(Side Effect) 없이 화면만 정상 렌더링합니다."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>책자리 관리자 - {title}</title>
        <style>
            body {{
                font-family: 'SUIT', sans-serif;
                background-color: #F5F5F8;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background-color: #FFFFFF;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.06);
                text-align: center;
                max-width: 480px;
                width: 100%;
            }}
            .icon {{
                font-size: 48px;
                margin-bottom: 20px;
            }}
            h1 {{
                color: #111827;
                font-size: 24px;
                margin-bottom: 12px;
                font-weight: 700;
            }}
            p {{
                color: #6B7280;
                font-size: 15px;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .status-btn {{
                background-color: #FDE68A;
                color: #F59E0B;
                padding: 14px 24px;
                border-radius: 12px;
                font-weight: 700;
                display: inline-block;
                border: none;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon">🤖</div>
            <h1>{title}</h1>
            <p>봇 요청이 감지되어 화면만 미리 렌더링되었습니다.<br>실제 관리자 화면에서 버튼을 직접 클릭해야 최종 처리가 완료됩니다.</p>
            <div class="status-btn">{status}</div>
        </div>
    </body>
    </html>
    """

def get_slug_by_tag(tag: str) -> str:
    """한글 태그명에 매핑되는 영어 슬러그를 반환합니다. 매핑이 없으면 그대로 반환합니다."""
    for item in ALL_TAXONOMY:
        if item.get("tag") == tag:
            return item.get("slug", tag)
    return tag

class ThreadsTriggerRequest(BaseModel):
    curation_tag: Optional[str] = None
    curation_title: Optional[str] = None
    age_group: Optional[str] = None

class WeeklyTriggerRequest(BaseModel):
    index: Optional[int] = None

def select_three_books(curation_tag: str) -> List[dict]:
    """도서 데이터베이스에서 조건에 맞는 책 3권을 엄선합니다. (confidence_score 내림차순)"""
    query = supabase.table("childbook_items").select("*")
    query = query.or_("is_hidden.is.null,is_hidden.eq.false")
    query = query.not_.is_("image_url", "null")
    query = query.neq("image_url", "")

    SPECIAL_TAGS = ['winter-vacation', 'summer-vacation', 'research-council', 'caldecott', '겨울방학2026', '여름방학2026', '어린이도서연구회']
    if curation_tag in SPECIAL_TAGS:
        query = query.ilike("curation_tag", f"%{curation_tag}%")
    else:
        or_filter = f'curation_tag.eq."{curation_tag}",curation_tag.like."{curation_tag},%",curation_tag.eq."#{curation_tag}",curation_tag.like."#{curation_tag},%"'
        query = query.or_(or_filter)

    # AI 태깅 신뢰도 높은 순으로 정렬 (ㄱㄴㄷ 정렬 버그 수정 — 특정 초성 도서가 고정 노출되는 현상 방지)
    query = query.order("confidence_score", desc=True)
    
    result = query.execute()
    books = result.data if result.data else []
    
    # 만약 해당 태그를 가진 도서가 3권보다 부족한 경우, 전체 도서 중에서 보충
    if len(books) < 3:
        needed = 3 - len(books)
        fallback_query = supabase.table("childbook_items").select("*")
        fallback_query = fallback_query.or_("is_hidden.is.null,is_hidden.eq.false")
        fallback_query = fallback_query.not_.is_("image_url", "null")
        fallback_query = fallback_query.neq("image_url", "")
        if books:
            book_ids = [b["id"] for b in books]
            fallback_query = fallback_query.not_.in_("id", book_ids)
        # 단순히 제목 오름차순 대신 전국 대출수(national_loan_count desc) 기준 우수 도서를 엄선하여 폴백 보충
        fallback_query = fallback_query.order("national_loan_count", desc=True).limit(needed)
        fallback_result = fallback_query.execute()
        if fallback_result.data:
            books.extend(fallback_result.data)
            
    return books[:3]

_TRIM_FILLER = " 아이의 호기심과 상상력을 풍부하게 키워주고 부모와 함께 읽으며 따뜻한 감동과 소중한 교훈을 배울 수 있는 그림책입니다."

def trim_text_fallback(text: str) -> str:
    """텍스트를 3줄을 꽉 채우는 60자 ~ 70자 범위의 자연스러운 문장으로 다듬습니다. (문장 완성형 종결 보장)"""
    sentences = text.replace("\r", "").split(".")
    sentences = [s.strip() for s in sentences if s.strip()]

    combined = []
    current_len = 0
    for s in sentences:
        if current_len + len(s) + 1 <= 68:
            combined.append(s + ".")
            current_len += len(s) + 1
        else:
            if not combined:
                combined.append(s[:64] + ".")
            break

    result = " ".join(combined)

    # 분량이 짧을 경우 뒤를 메워 3줄을 꽉 채움 (filler는 어떤 짧은 입력도 75자 이상 보장)
    if len(result) < 75:
        result = result + _TRIM_FILLER
        if len(result) > 85:
            cut = result[:86].rfind(" ")
            result = result[:cut] if cut >= 60 else result[:85]
        if not result.endswith("."):
            result = result.rstrip() + "."

    # 존댓말 종결 보정 — 어절 경계에서 잘라 "이야기입니다." 추가
    if not result.endswith("다."):
        trim_at = min(len(result), 78)
        last_space = result[:trim_at].rfind(" ")
        cut = last_space if last_space >= 40 else trim_at
        result = result[:cut].rstrip() + " 이야기입니다."
    return result

async def process_telegram_feedback(feedback_text: str):
    """사용자가 텔레그램 방에 보낸 피드백 텍스트를 기반으로 오늘자 미승인 피드를 수정하여 재생성합니다."""
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    today_str = datetime.datetime.now(tz_kst).strftime("%Y-%m-%d")
    
    db_result = supabase.table("threads_feeds")\
        .select("*")\
        .eq("is_approved", False)\
        .gte("created_at", f"{today_str}T00:00:00+09:00")\
        .order("id", desc=True)\
        .limit(1)\
        .execute()
        
    if not db_result.data:
        print("⚠️ 피드백을 반영할 오늘자 미승인 피드 레코드가 존재하지 않습니다.")
        return
        
    feed = db_result.data[0]
    feed_id = feed["id"]
    book_ids = feed["book_ids"]
    old_caption = feed["content"]
    old_descriptions = feed.get("card_descriptions", []) or []
    
    await send_telegram_message("⏳ <b>피드백을 반영하여 카드뉴스 텍스트를 수정하고 있습니다. 잠시만 기다려 주세요...</b>")
    
    books_result = supabase.table("childbook_items").select("*").in_("id", book_ids).execute()
    books_data = books_result.data if books_result.data else []
    
    id_map = {b["id"]: b for b in books_data}
    books = [id_map[bid] for bid in book_ids if bid in id_map]
    
    new_content = await apply_feedback_with_gemini(
        feedback_text=feedback_text,
        old_caption=old_caption,
        old_descriptions=old_descriptions,
        books=books
    )
    
    if not new_content:
        await send_telegram_message("❌ AI 수정 중 오류가 발생했습니다. 다시 시도해 주세요.")
        return
        
    supabase.table("threads_feeds").update({
        "content": new_content["caption"],
        "card_descriptions": new_content["card_descriptions"]
    }).eq("id", feed_id).execute()
    
    backend_url = get_backend_url()
    confirm_url = _build_admin_url(backend_url, "/api/threads/approve-text", feed_id, sign_action("approve-text", feed_id))
    
    books_list = []
    for idx, b in enumerate(books):
        desc = new_content["card_descriptions"][idx] if idx < len(new_content["card_descriptions"]) else ""
        books_list.append({
            "title": b.get("title", "제목"),
            "publisher": b.get("publisher", "출판사"),
            "description": desc
        })
        
    await send_telegram_message("✨ <b>수정이 완료되었습니다. 아래 새로운 시안을 확인해 주세요.</b>")
    await send_threads_text_preview(
        caption=new_content["caption"],
        books=books_list,
        confirm_url=confirm_url
    )

async def check_if_listener_should_run() -> bool:
    """오늘 날짜에 생성된 미승인 피드가 Supabase DB에 존재하는지 확인합니다."""
    try:
        tz_kst = datetime.timezone(datetime.timedelta(hours=9))
        today_str = datetime.datetime.now(tz_kst).strftime("%Y-%m-%d")
        
        db_result = supabase.table("threads_feeds")\
            .select("id")\
            .eq("is_approved", False)\
            .gte("created_at", f"{today_str}T00:00:00+09:00")\
            .limit(1)\
            .execute()
        return bool(db_result.data)
    except Exception as e:
        print(f"❌ 리스너 상태 확인 실패: {e}")
        return False

async def telegram_feedback_listener():
    """텔레그램 getUpdates API를 조건부로 풀링하여 사용자가 보낸 피드백 텍스트를 감지하고 반영합니다.
    월/수/금 시안 전송 직후(오늘의 미승인 피드가 DB에 존재할 때)부터 최종 승인 완료 시까지만 활성화됩니다.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("⚠️ TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 없어 텔레그램 피드백 리스너를 시작하지 않습니다.")
        return
        
    print("🤖 [Telegram Feedback Listener] 백그라운드 태스크 가동 시작...")
    offset = None
    api_base = f"https://api.telegram.org/bot{bot_token}"
    
    async with httpx.AsyncClient() as client:
        while True:
            # 1. 텔레그램 폴링을 활성화할 타이밍인지 DB 상태 확인
            should_run = await check_if_listener_should_run()
            if not should_run:
                # 비활성 상태일 때는 API 호출을 차단하고 10초 대기
                await asyncio.sleep(10)
                continue
                
            # 2. 활성 상태인 경우 3초 주기로 폴링 수행
            try:
                params = {"timeout": 10}
                if offset is not None:
                    params["offset"] = offset
                    
                response = await client.get(f"{api_base}/getUpdates", params=params, timeout=15.0)
                if response.status_code == 200:
                    res_json = response.json()
                    if res_json.get("ok"):
                        updates = res_json.get("result", [])
                        for update in updates:
                            update_id = update["update_id"]
                            offset = update_id + 1
                            
                            message = update.get("message")
                            if not message:
                                continue
                                
                            text = message.get("text")
                            from_chat_id = str(message.get("chat", {}).get("id"))
                            msg_date = message.get("date") # Unix timestamp
                            
                            # 최근 30분 이내의 메시지만 처리하도록 안전장치 확보
                            current_time = time.time()
                            is_recent = (current_time - msg_date) < 1800 if msg_date else False
                            
                            if text and from_chat_id == chat_id and not text.startswith("/") and is_recent:
                                print(f"💬 [Telegram Feedback] 사용자 피드백 감지: '{text}'")
                                await process_telegram_feedback(text)
            except Exception as e:
                print(f"❌ [Telegram Feedback Listener] 에러 발생: {e}")
                
            await asyncio.sleep(3)

async def execute_weekly_threads_generation(index: int, curation_tag: Optional[str] = None, curation_title: Optional[str] = None):
    """지정된 주간 큐레이션 인덱스를 사용해 도서 선정 ➔ 텍스트 시안 생성 ➔ 텔레그램 전송을 수행합니다."""
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    now_date = datetime.datetime.now(tz_kst).date()
    
    curations = get_weekly_curations(now_date)
    if not curations or index >= len(curations):
        raise ValueError(f"해당 인덱스({index})의 주간 큐레이션이 존재하지 않습니다.")
        
    curation = curations[index]
    c_tag = (curation_tag or curation["tag"]).lstrip("#")
    c_title = curation_title or curation["title"]
    
    print(f"📚 [스레드 발행 파이프라인] 테마: '{c_title}' (태그: '{c_tag}') 작업 시작")
    
    # 7-Book Rule 가드레일: 첫 번째 태그 정밀 매칭 기준 7권 이상 확보되지 않은 큐레이션은 스레드 콘텐츠 발행 불가
    from core.taxonomy import check_7_books_exist
    if not check_7_books_exist(c_tag):
        raise ValueError(f"큐레이션 태그 '{c_tag}'는 첫 번째 태그 정밀 매칭 기준 7권 이상 확보되지 않아 스레드 콘텐츠로 발행할 수 없습니다.")
        
    books = select_three_books(c_tag)
    if len(books) < 3:
        raise ValueError(f"큐레이션 도서가 부족합니다. 최소 3권의 도서가 필요합니다.")
        
    ai_content = generate_ai_threads_content(c_title, c_tag, books)
    
    db_result = supabase.table("threads_feeds").insert({
        "title": c_title,
        "content": ai_content["caption"],
        "curation_tag": c_tag,
        "book_ids": [b["id"] for b in books],
        "card_descriptions": ai_content["card_descriptions"],
        "is_approved": False
    }).execute()
    
    if not db_result.data:
        raise RuntimeError("Supabase에 피드 데이터를 삽입하는 데 실패했습니다.")
        
    feed_id = db_result.data[0]["id"]
    
    backend_url = get_backend_url()
    confirm_url = _build_admin_url(backend_url, "/api/threads/approve-text", feed_id, sign_action("approve-text", feed_id))
    
    books_list = []
    for idx, b in enumerate(books):
        desc = ai_content["card_descriptions"][idx] if idx < len(ai_content["card_descriptions"]) else ""
        books_list.append({
            "title": b.get("title", "제목"),
            "publisher": b.get("publisher", "출판사"),
            "description": desc
        })
        
    await send_threads_text_preview(
        caption=ai_content["caption"],
        books=books_list,
        confirm_url=confirm_url
    )
    print(f"✅ [스레드 발행 파이프라인] 1단계 텍스트 시안 텔레그램 전송 완료. Feed ID: {feed_id}")
    return feed_id

def validate_curation_tag(tag: Optional[str]):
    if not tag:
        return
    SPECIAL_TAGS = ['winter-vacation', 'summer-vacation', 'research-council', 'caldecott', '겨울방학2026', '여름방학2026', '어린이도서연구회']
    valid_tags = {item["tag"] for item in ALL_TAXONOMY}
    valid_tags.update(SPECIAL_TAGS)
    clean_tag = tag.lstrip("#")
    if clean_tag not in valid_tags and tag not in valid_tags:
        raise HTTPException(status_code=400, detail="유효하지 않은 큐레이션 태그입니다.")

@router.get("/trigger-weekly")
async def trigger_weekly_get(
    request: Request,
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
    index: Optional[int] = Query(None, description="주간 큐레이션 인덱스 (0: 월, 1: 수, 2: 금)"),
    curation_tag: Optional[str] = Query(None, description="커스텀 큐레이션 태그"),
    curation_title: Optional[str] = Query(None, description="커스텀 큐레이션 타이틀")
):
    """수동으로 1단계 텍스트 시안 및 이미지 생성 요청을 텔레그램으로 보냅니다."""
    # 1. 외부 스크랩 봇 감지 시 실행 우회 (Side Effect 방지)
    if is_scrap_bot(request):
        print("🤖 [Bot Filter] 스크랩 봇 요청 감지 (/api/threads/trigger-weekly) -> 실행 우회")
        return {"status": "success", "message": "Bot request bypassed", "feed_id": None}

    # 2. 관리자 인증 토큰 검증
    _require_admin_token(x_admin_token)
    validate_curation_tag(curation_tag)
    
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    now_kst = datetime.datetime.now(tz_kst)
    
    target_idx = index
    if target_idx is None:
        weekday = now_kst.weekday()
        if weekday == 0:
            target_idx = 0
        elif weekday == 2:
            target_idx = 1
        elif weekday == 4:
            target_idx = 2
        else:
            target_idx = 0
            
    try:
        feed_id = await execute_weekly_threads_generation(
            index=target_idx,
            curation_tag=curation_tag,
            curation_title=curation_title
        )
        return {"status": "success", "message": "1단계 텍스트 시안 발송 완료", "feed_id": feed_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-weekly")
async def trigger_weekly_post(
    req: WeeklyTriggerRequest,
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
):
    """수동으로 1단계 텍스트 시안 및 이미지 생성 요청을 텔레그램으로 보냅니다. (POST 호출 대응)"""
    _require_admin_token(x_admin_token)
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    now_kst = datetime.datetime.now(tz_kst)
    
    target_idx = req.index
    if target_idx is None:
        weekday = now_kst.weekday()
        if weekday == 0:
            target_idx = 0
        elif weekday == 2:
            target_idx = 1
        elif weekday == 4:
            target_idx = 2
        else:
            target_idx = 0
            
    try:
        feed_id = await execute_weekly_threads_generation(index=target_idx)
        return {"status": "success", "message": "1단계 텍스트 시안 발송 완료", "feed_id": feed_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ApproveSubmitRequest(BaseModel):
    feed_id: int
    signature: str

async def publish_approved_feed(feed_id: int):
    """최종 승인된 피드를 즉시 Threads 채널에 발행합니다. (늦은 승인 대응)"""
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    from services.threads_publisher import publish_carousel_to_threads, publish_reply_to_threads
    
    feed_result = supabase.table("threads_feeds").select("*").eq("id", feed_id).execute()
    if not feed_result.data:
        print(f"❌ [즉시 배포] 피드 {feed_id}가 존재하지 않습니다.")
        return

    feed = feed_result.data[0]
    caption = feed["content"]
    image_urls = feed["image_urls"]
    
    if not image_urls:
        print(f"❌ [즉시 배포] 피드 {feed_id}에 이미지 URL이 없습니다.")
        return
        
    # 원자적 선점(Atomic Claim)
    now_str = datetime.datetime.now(tz_kst).isoformat()
    claim_result = supabase.table("threads_feeds").update({
        "published_at": now_str
    }).eq("id", feed_id).is_("published_at", "null").execute()
    
    if not claim_result.data:
        print(f"⚠️ [즉시 배포] 피드 {feed_id}가 이미 발행 중이거나 선점됨")
        return
        
    # 404 리다이렉트 스모크 테스트 선행 수행 (부모 캐러셀 발행 전 차단)
    curation_tag = feed.get("curation_tag") or "추천"
    tag_clean = curation_tag.lstrip("#")
    slug = get_slug_by_tag(tag_clean)
    reply_text = f"🔗 https://checkjari.com/c/{slug}"

    print(f"📣 [즉시 배포] 피드 {feed_id} 즉시 발행 개시")
    await send_telegram_message(f"📢 <b>[즉시 배포]</b> 늦은 승인이 감지되었습니다. 피드 ID: {feed_id}의 Threads 최종 배포를 즉시 시작합니다...")
    
    # [마케팅 전략 변경] 첫 댓글 등록을 하지 않으므로 단축 URL 스모크 테스트 생략
    # try:
    #     from services.threads_publisher import smoke_test_short_url
    #     await smoke_test_short_url(reply_text)
    # except Exception as smoke_err:
    #     print(f"❌ [즉시 배포] 스모크 테스트 실패: {smoke_err}")
    #     await send_telegram_message(f"🚨 <b>[발행 차단]</b> 리다이렉트 링크가 404 상태입니다. 배포를 중단했습니다.\n원인: {smoke_err}")
    #     try:
    #         supabase.table("threads_feeds").update({
    #             "published_at": None
    #         }).eq("id", feed_id).execute()
    #     except Exception as rollback_err:
    #         print(f"❌ [즉시 배포] 피드({feed_id}) 선점 롤백 실패: {rollback_err}")
    #     return

    try:
        post_id = await publish_carousel_to_threads(text=caption, image_urls=image_urls)
    except Exception as publish_err:
        try:
            supabase.table("threads_feeds").update({
                "published_at": None
            }).eq("id", feed_id).execute()
        except Exception as rollback_err:
            print(f"❌ [즉시 배포] 피드({feed_id}) 선점 롤백 실패: {rollback_err}")
        print(f"❌ [즉시 배포] 피드({feed_id}) Threads 발행 실패: {publish_err}")
        await send_telegram_message(f"❌ <b>[즉시 배포 오류]</b> 피드({feed_id}) 발행 실패: {publish_err}")
        return
        
    # [마케팅 전략 변경] 첫 댓글 연동 생략 ('스하리' 유도로 전환)
    # try:
    #     await publish_reply_to_threads(parent_post_id=post_id, reply_text=reply_text)
    # except Exception as reply_err:
    #     print(f"❌ [즉시 배포] 첫 댓글 등록 실패: {reply_err}")
    #     await send_telegram_message(f"⚠️ [즉시 배포 경고] 피드 발행 성공, 첫 댓글 실패: {reply_err}")
        
    await send_telegram_message(f"🎉 <b>[즉시 배포 완료]</b> Threads에 최종 배포 성공. 포스트 ID: <code>{post_id}</code>")

@router.get("/approve-text", response_class=HTMLResponse)
async def approve_text_view(request: Request, feed_id: int, signature: str):
    """1단계 승인 확인 화면을 렌더링합니다. (봇 링크 크롤링에 무해함)"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>책자리 관리자 - 1단계 텍스트 승인</title>
        <style>
            body {{
                font-family: 'SUIT', sans-serif;
                background-color: #F5F5F8;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background-color: #FFFFFF;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.06);
                text-align: center;
                max-width: 480px;
                width: 100%;
            }}
            .icon {{ font-size: 48px; margin-bottom: 20px; }}
            h1 {{ color: #111827; font-size: 24px; margin-bottom: 12px; font-weight: 700; }}
            p {{ color: #6B7280; font-size: 15px; line-height: 1.6; margin-bottom: 30px; }}
            .btn {{
                background-color: #F59E0B;
                color: #FFFFFF;
                padding: 14px 24px;
                border-radius: 12px;
                font-weight: 700;
                display: inline-block;
                border: none;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }}
            .btn:disabled {{ background-color: #E5E7EB; color: #9CA3AF; cursor: not-allowed; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon">📝</div>
            <h1>1단계 텍스트 승인</h1>
            <p>작성된 큐레이션 카드뉴스 텍스트 시안을 승인하시겠습니까?<br>승인 시 최종 카드뉴스 이미지 5장이 생성되어 2차 검수 알림이 발송됩니다.</p>
            <button id="submit-btn" class="btn" onclick="submitApprove()">승인하고 이미지 생성하기</button>
        </div>
        <script>
            async function submitApprove() {{
                const btn = document.getElementById("submit-btn");
                btn.disabled = true;
                btn.innerText = "처리 중...";
                try {{
                    const res = await fetch("/api/threads/approve-text/submit", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ feed_id: {feed_id}, signature: "{signature}" }})
                    }});
                    const data = await res.json();
                    if (res.ok) {{
                        alert("승인이 완료되었습니다. 이미지 생성이 완료되면 텔레그램으로 2차 시안이 발송됩니다.");
                        window.close();
                    }} else {{
                        alert("오류 발생: " + (data.detail || "인증 실패"));
                        btn.disabled = false;
                        btn.innerText = "승인하고 이미지 생성하기";
                    }}
                }} catch (e) {{
                    alert("네트워크 오류 발생");
                    btn.disabled = false;
                    btn.innerText = "승인하고 이미지 생성하기";
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/approve-text/submit")
async def approve_text_submit(req: ApproveSubmitRequest):
    """1단계 승인 처리: 실제 카드뉴스 이미지를 렌더링하고 업로드하여 2단계 검수 요청을 텔레그램으로 발송합니다."""
    if not verify_action_signature("approve-text", req.feed_id, req.signature):
        raise HTTPException(status_code=401, detail="유효하지 않은 관리자 서명입니다.")
        
    feed_id = req.feed_id
    feed_result = supabase.table("threads_feeds").select("*").eq("id", feed_id).execute()
    if not feed_result.data:
        raise HTTPException(status_code=404, detail="해당 피드 레코드를 찾을 수 없습니다.")
        
    feed = feed_result.data[0]
    book_ids = feed["book_ids"]
    curation_title = feed["title"]
    caption = feed["content"]
    card_descriptions = feed.get("card_descriptions", []) or []
    
    books_result = supabase.table("childbook_items").select("*").in_("id", book_ids).execute()
    books_data = books_result.data if books_result.data else []
    id_map = {b["id"]: b for b in books_data}
    books = [id_map[bid] for bid in book_ids if bid in id_map]
    
    image_urls = []
    
    # 텔레그램에 이미지 렌더링 시작 알림
    await send_telegram_message("🎨 <b>카드뉴스 이미지 생성 및 Supabase Storage 업로드를 시작합니다. 약 10~20초 소요됩니다...</b>")
    
    for idx, b in enumerate(books):
        desc = card_descriptions[idx] if idx < len(card_descriptions) else ""
        card_img = generate_card_news(
            title=b.get("title", "제목"),
            author="",
            publisher=b.get("publisher", "출판사"),
            cover_url=b.get("image_url", ""),
            description=desc,
            curation_title=curation_title
        )
        
        file_name = f"threads_feeds/{feed_id}/{uuid.uuid4()}.png"
        public_url = await upload_image_to_supabase(card_img, file_name)
        image_urls.append(public_url)
        
    supabase.table("threads_feeds").update({
        "image_urls": image_urls
    }).eq("id", feed_id).execute()
    
    backend_url = get_backend_url()
    confirm_url = _build_admin_url(backend_url, "/api/threads/approve", feed_id, sign_action("approve", feed_id))
    
    await send_threads_preview(
        caption=caption,
        image_urls=image_urls,
        confirm_url=confirm_url
    )
    return {"status": "success", "message": "카드뉴스 이미지 생성 및 2차 전송 완료"}

@router.get("/approve", response_class=HTMLResponse)
async def approve_feed_view(request: Request, feed_id: int, signature: str):
    """2단계 최종 승인 확인 화면을 렌더링합니다."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>책자리 관리자 - 최종 발행 승인</title>
        <style>
            body {{
                font-family: 'SUIT', sans-serif;
                background-color: #F5F5F8;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background-color: #FFFFFF;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.06);
                text-align: center;
                max-width: 480px;
                width: 100%;
            }}
            .icon {{ font-size: 48px; margin-bottom: 20px; }}
            h1 {{ color: #111827; font-size: 24px; margin-bottom: 12px; font-weight: 700; }}
            p {{ color: #6B7280; font-size: 15px; line-height: 1.6; margin-bottom: 30px; }}
            .btn {{
                background-color: #F59E0B;
                color: #FFFFFF;
                padding: 14px 24px;
                border-radius: 12px;
                font-weight: 700;
                display: inline-block;
                border: none;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }}
            .btn:disabled {{ background-color: #E5E7EB; color: #9CA3AF; cursor: not-allowed; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon">🚀</div>
            <h1>최종 발행 승인</h1>
            <p>2차 이미지 검수 완료 후 최종 발행 예약을 확정하시겠습니까?<br>승인 시 정규 시각(밤 9시 30분)에 자동 발행되며, 21시 30분을 경과했다면 즉시 발행됩니다.</p>
            <button id="submit-btn" class="btn" onclick="submitApprove()">최종 승인 및 발행 예약</button>
        </div>
        <script>
            async function submitApprove() {{
                const btn = document.getElementById("submit-btn");
                btn.disabled = true;
                btn.innerText = "처리 중...";
                try {{
                    const res = await fetch("/api/threads/approve/submit", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ feed_id: {feed_id}, signature: "{signature}" }})
                    }});
                    const data = await res.json();
                    if (res.ok) {{
                        alert("최종 발행 승인이 확정되었습니다.");
                        window.close();
                    }} else {{
                        alert("오류 발생: " + (data.detail || "인증 실패"));
                        btn.disabled = false;
                        btn.innerText = "최종 승인 및 발행 예약";
                    }}
                }} catch (e) {{
                    alert("네트워크 오류 발생");
                    btn.disabled = false;
                    btn.innerText = "최종 승인 및 발행 예약";
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/approve/submit")
async def approve_feed_submit(req: ApproveSubmitRequest):
    """2단계 최종 승인 처리: 발행 예약 처리 또는 늦은 승인 시 즉시 발행 트리거"""
    if not verify_action_signature("approve", req.feed_id, req.signature):
        raise HTTPException(status_code=401, detail="유효하지 않은 관리자 서명입니다.")
        
    feed_id = req.feed_id
    db_result = supabase.table("threads_feeds").update({
        "is_approved": True
    }).eq("id", feed_id).execute()
    
    if not db_result.data:
        raise HTTPException(status_code=404, detail="해당 피드 레코드를 찾을 수 없습니다.")
        
    # KST 시간 확인 및 즉시 발행 분기 적용 (밤 9시 30분 기준)
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    now_kst = datetime.datetime.now(tz_kst)
    
    if (now_kst.hour > 21) or (now_kst.hour == 21 and now_kst.minute >= 30):
        # 밤 9시 30분 이후 늦은 승인이므로 즉시 발행을 수행 (백그라운드 차단 방지 위해 비동기로 실행 호출)
        asyncio.create_task(publish_approved_feed(feed_id))
        return {"status": "success", "message": "늦은 승인이 감지되어 Threads 채널로 즉시 배포를 시작합니다."}
        
    await send_telegram_message("🚀 <b>주간 큐레이션 발행 승인이 최종 완료되었습니다!</b> 오늘 밤 9시 30분 정규 스케줄(육퇴 골든타임)에 자동으로 Threads로 최종 발행됩니다.")
    return {"status": "success", "message": "발행 예약 확정 완료"}

async def weekly_threads_scheduler():
    """매분마다 시간을 감지하여 월/수/금 오후 1시(13:00)에는 텍스트 시안을 자동 빌드하고, 밤 9시 30분(육퇴 골든타임)에는 최종 승인된 피드를 발행합니다."""
    print("⏰ [Weekly Threads Scheduler] 스케줄러 태스크 가동 시작...")
    
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    
    # 중복 실행 방지용 메모리 락 (당일 한 번만 실행)
    last_trigger_date_1pm = None
    last_trigger_date_930pm = None
    
    while True:
        try:
            now_kst = datetime.datetime.now(tz_kst)
            today_date = now_kst.date()
            weekday = now_kst.weekday()  # 0: 월, 2: 수, 4: 금
            
            # 1. 월/수/금요일 오후 1시 (13:00) -> 1단계 텍스트 시안 생성 및 텔레그램 발송
            # minute==0 정확 일치는 루프 드리프트(sleep 60초 + 처리 시간)로 트리거를 통째로 놓칠 수 있어 hour 단위로 판정
            if weekday in (0, 2, 4) and now_kst.hour == 13:
                if last_trigger_date_1pm != today_date:
                    last_trigger_date_1pm = today_date  # 실패 여부와 무관하게 1일 1회만 시도 (매분 재시도 스팸 방지)
                    print(f"📡 [스케줄러] 오후 1시 감지. 요일: {weekday}, 날짜: {today_date} -> 1단계 텍스트 시안 생성 시작")
                    target_idx = 0 if weekday == 0 else (1 if weekday == 2 else 2)
                    try:
                        # 이미 오늘 동일 큐레이션 태그로 생성된 피드가 있는지 재검증
                        today_str = today_date.strftime("%Y-%m-%d")
                        target_idx = 0 if weekday == 0 else (1 if weekday == 2 else 2)
                        curations = get_weekly_curations(today_date)
                        c_tag = curations[target_idx]["tag"].lstrip("#") if target_idx < len(curations) else ""
                        
                        dup = supabase.table("threads_feeds").select("id")\
                            .eq("curation_tag", c_tag)\
                            .gte("created_at", f"{today_str}T00:00:00+09:00")\
                            .limit(1).execute()
                        if not dup.data:
                            await execute_weekly_threads_generation(index=target_idx)
                    except Exception as e:
                        print(f"❌ [스케줄러] 1시 1단계 생성 중 에러: {e}")
                        await send_telegram_message(f"❌ [스케줄러 경고] 오후 1시 1단계 시안 생성 실패: {e}")
                        
            # 2. 월/수/금요일 밤 9시 30분 (21:30~21:59) -> 승인된 카드뉴스 최종 배포 (육퇴 골든타임)
            if weekday in (0, 2, 4) and now_kst.hour == 21 and now_kst.minute >= 30:
                if last_trigger_date_930pm != today_date:
                    last_trigger_date_930pm = today_date  # 실패 여부와 무관하게 1일 1회만 시도 (매분 재시도 스팸 방지)
                    print(f"📡 [스케줄러] 밤 9시 30분 감지. 요일: {weekday}, 날짜: {today_date} -> 최종 배포 스캔")
                    try:
                        today_str = today_date.strftime("%Y-%m-%d")
                        approved_result = supabase.table("threads_feeds").select("*")\
                            .eq("is_approved", True)\
                            .is_("published_at", "null")\
                            .gte("created_at", f"{today_str}T00:00:00+09:00")\
                            .order("id", desc=True)\
                            .limit(1).execute()
                            
                        if approved_result.data:
                            feed = approved_result.data[0]
                            feed_id = feed["id"]
                            caption = feed["content"]
                            image_urls = feed["image_urls"]

                            if image_urls:
                                # 원자적 선점(Atomic Claim): published_at을 먼저 설정하여 다른 프로세스의 중복 발행을 차단
                                # published_at IS NULL인 경우에만 업데이트가 성공하므로, 이미 선점된 경우 data가 비어 반환됨
                                now_str = datetime.datetime.now(tz_kst).isoformat()
                                claim_result = supabase.table("threads_feeds").update({
                                    "published_at": now_str
                                }).eq("id", feed_id).is_("published_at", "null").execute()

                                if not claim_result.data:
                                    print(f"⚠️ [스케줄러] 피드({feed_id})가 이미 다른 프로세스에 의해 선점됨 → 중복 발행 차단")
                                    continue

                                curation_tag = feed.get("curation_tag") or "추천"
                                tag_clean = curation_tag.lstrip("#")
                                slug = get_slug_by_tag(tag_clean)
                                reply_text = f"🔗 https://checkjari.com/c/{slug}"

                                print(f"📣 [스케줄러] 최종 승인된 피드({feed_id}) 배포 진행")
                                await send_telegram_message("📢 <b>[스케줄러] 최종 승인된 카드뉴스의 Threads 최종 배포를 진행합니다...</b>")
                                
                                # [마케팅 전략 변경] 첫 댓글 등록을 하지 않으므로 단축 URL 스모크 테스트 생략
                                # try:
                                #     from services.threads_publisher import smoke_test_short_url
                                #     await smoke_test_short_url(reply_text)
                                # except Exception as smoke_err:
                                #     print(f"❌ [스케줄러] 스모크 테스트 실패: {smoke_err}")
                                #     await send_telegram_message(f"🚨 <b>[발행 차단]</b> 리다이렉트 링크가 404 상태입니다. 배포를 중단했습니다.\n원인: {smoke_err}")
                                #     try:
                                #         supabase.table("threads_feeds").update({
                                #             "published_at": None
                                #         }).eq("id", feed_id).execute()
                                #     except Exception as rollback_err:
                                #         print(f"❌ [스케줄러] 피드({feed_id}) 선점 롤백 실패: {rollback_err}")
                                #     continue

                                try:
                                    post_id = await publish_carousel_to_threads(text=caption, image_urls=image_urls)
                                except Exception as publish_err:
                                    # 발행 실패 시 선점 롤백: published_at을 되돌려 피드 유실을 막고 수동 재발행(/republish)이 가능하도록 복구
                                    try:
                                        supabase.table("threads_feeds").update({
                                            "published_at": None
                                        }).eq("id", feed_id).execute()
                                    except Exception as rollback_err:
                                        print(f"❌ [스케줄러] 피드({feed_id}) 선점 롤백 실패: {rollback_err}")
                                    print(f"❌ [스케줄러] 피드({feed_id}) Threads 발행 실패: {publish_err}")
                                    await send_telegram_message(
                                        f"❌ <b>[스케줄러 오류]</b> 피드({feed_id}) Threads 발행에 실패했습니다: {publish_err}\n\n"
                                        f"선점이 해제되었으므로 <code>POST /api/threads/republish/{feed_id}</code>로 수동 재발행할 수 있습니다."
                                    )
                                    continue

                                # [마케팅 전략 변경] 첫 댓글 자동 연동 생략 ('스하리' 유도로 전환)
                                # try:
                                #     await publish_reply_to_threads(parent_post_id=post_id, reply_text=reply_text)
                                #     print(f"✅ [스케줄러] 첫 댓글 등록 성공 (태그: {curation_tag} -> 슬러그: {slug})")
                                # except Exception as reply_err:
                                #     print(f"❌ [스케줄러] 첫 댓글 등록 실패: {reply_err}")
                                #     await send_telegram_message(f"⚠️ [스케줄러 경고] 피드({feed_id}) 발행에는 성공했으나, 첫 댓글 등록 중 오류 발생: {reply_err}")

                                await send_telegram_message(f"🎉 <b>[실시간 배포 완료]</b> Threads에 최종 배포되었습니다. 포스트 ID: <code>{post_id}</code>")
                            else:
                                print(f"⚠️ [스케줄러] 피드({feed_id})가 승인되었으나 이미지 URL이 존재하지 않아 배포를 생략합니다.")
                                await send_telegram_message(f"⚠️ [스케줄러 경고] 피드({feed_id})가 승인되었으나 이미지 URL이 없어 배포되지 못했습니다.")
                        else:
                            print("ℹ️ [스케줄러] 오늘 승인된 예약 발행용 피드가 발견되지 않았습니다. 발행을 건너뜁니다.")
                            await send_telegram_message("ℹ️ <b>[스케줄러 알림]</b> 오늘 정규 발행 예약 건 중 승인 완료된(Okay) 피드가 없어 발행이 생략되었습니다.")
                    except Exception as e:
                        print(f"❌ [스케줄러] 밤 9시 30분 최종 배포 에러: {e}")
                        await send_telegram_message(f"❌ [스케줄러 오류] 밤 9시 30분 최종 발행 중 에러 발생: {e}")
                        
        except Exception as e:
            print(f"❌ [Weekly Threads Scheduler Loop Error]: {e}")
            
        await asyncio.sleep(60) # 1분 간격 체크


@router.get("/debug-telegram")
async def debug_telegram(
    request: Request,
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
):
    import os
    import httpx
    _require_admin_token(x_admin_token)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    backend_url = os.getenv("BACKEND_URL")
    
    status_info = {
        "bot_token_configured": bool(bot_token),
        "bot_token_length": len(bot_token) if bot_token else 0,
        "chat_id_configured": bool(chat_id),
        "chat_id_value": chat_id,
        "backend_url_configured": bool(backend_url),
        "backend_url_value": backend_url,
    }
    
    if not bot_token or not chat_id:
        return {"status": "error", "message": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured", "details": status_info}
        
    api_base = f"https://api.telegram.org/bot{bot_token}"
    async with httpx.AsyncClient() as client:
        try:
            # 1. 봇 정보 확인 테스트 (getMe)
            me_res = await client.get(f"{api_base}/getMe", timeout=5.0)
            me_data = me_res.json()
            
            # 2. 테스트 텍스트 메시지 발송 시도
            msg_res = await client.post(
                f"{api_base}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "🛠️ [Render 상용 서버 디버그] 텔레그램 메시지 발송 테스트 성공!"
                },
                timeout=5.0
            )
            msg_data = msg_res.json()
            
            # 3. 인라인 키보드 버튼을 포함한 메시지 발송 테스트 (URL 정책 확인용)
            confirm_url = _build_admin_url(
                get_backend_url(),
                "/api/threads/approve-text",
                0,
                sign_action("approve-text", 0),
            )
            btn_res = await client.post(
                f"{api_base}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"🛠️ [Render 상용 서버 디버그] 인라인 버튼 전송 테스트\nURL: {confirm_url}",
                    "reply_markup": {
                        "inline_keyboard": [[{"text": "테스트 승인", "url": confirm_url}]]
                    }
                },
                timeout=5.0
            )
            btn_data = btn_res.json()
            
            return {
                "status": "success",
                "details": status_info,
                "getMe": me_data,
                "sendMessage_simple": msg_data,
                "sendMessage_button": btn_data
            }
        except Exception as e:
            return {"status": "error", "message": str(e), "details": status_info}


@router.post("/republish/{feed_id}")
async def republish_feed(
    feed_id: int,
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
):
    """
    특정 feed_id의 피드를 수동으로 즉시 재발행합니다.
    스케줄러 오류 등으로 인해 발행되지 못한 피드를 복구할 때 사용합니다.
    """
    _require_admin_token(x_admin_token)
    import datetime
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))

    feed_result = supabase.table("threads_feeds").select("*").eq("id", feed_id).execute()
    if not feed_result.data:
        raise HTTPException(status_code=404, detail=f"피드 ID {feed_id}를 찾을 수 없습니다.")

    feed = feed_result.data[0]

    if feed.get("published_at"):
        raise HTTPException(status_code=400, detail=f"피드 ID {feed_id}는 이미 발행된 피드입니다. (published_at: {feed['published_at']})")

    if not feed.get("is_approved"):
        raise HTTPException(status_code=400, detail=f"피드 ID {feed_id}는 아직 승인되지 않은 피드입니다.")

    image_urls = feed.get("image_urls") or []
    if not image_urls:
        raise HTTPException(status_code=400, detail=f"피드 ID {feed_id}에 이미지 URL이 없습니다.")

    caption = feed.get("content", "")

    curation_tag = feed.get("curation_tag") or "추천"
    tag_clean = curation_tag.lstrip("#")
    slug = get_slug_by_tag(tag_clean)
    reply_text = f"🔗 https://checkjari.com/c/{slug}"

    try:
        await send_telegram_message(f"🔄 <b>[수동 재발행]</b> 피드 ID {feed_id} 재발행을 시작합니다...")
        
        # [마케팅 전략 변경] 첫 댓글 등록을 하지 않으므로 단축 URL 스모크 테스트 생략
        # from services.threads_publisher import smoke_test_short_url
        # await smoke_test_short_url(reply_text)
    except Exception as smoke_err:
        pass
        print(f"❌ [수동 재발행] 스모크 테스트 실패: {smoke_err}")
        await send_telegram_message(f"🚨 <b>[수동 재발행 차단]</b> 리다이렉트 링크가 404 상태입니다. 배포를 중단했습니다.\n원인: {smoke_err}")
        raise HTTPException(status_code=500, detail=f"스모크 테스트 실패: {smoke_err}")

    try:
        post_id = await publish_carousel_to_threads(text=caption, image_urls=image_urls)
        
        # [마케팅 전략 변경] 첫 댓글 자동 연동 생략 ('스하리' 유도로 전환)
        # try:
        #     await publish_reply_to_threads(parent_post_id=post_id, reply_text=reply_text)
        #     print(f"✅ [수동 재발행] 첫 댓글 등록 성공 (태그: {curation_tag} -> 슬러그: {slug})")
        # except Exception as reply_err:
        #     print(f"❌ [수동 재발행] 첫 댓글 등록 실패: {reply_err}")
        #     await send_telegram_message(f"⚠️ [재발행 경고] 피드({feed_id}) 발행에는 성공했으나, 첫 댓글 등록 중 오류 발생: {reply_err}")

        supabase.table("threads_feeds").update(
            {"published_at": datetime.datetime.now(tz_kst).isoformat()}
        ).eq("id", feed_id).execute()

        await send_telegram_message(f"🎉 <b>[수동 재발행 완료]</b> 피드 ID {feed_id} 발행 성공. 포스트 ID: <code>{post_id}</code>")
        return {"status": "success", "feed_id": feed_id, "post_id": post_id}

    except Exception as e:
        await send_telegram_message(f"❌ <b>[수동 재발행 실패]</b> 피드 ID {feed_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
