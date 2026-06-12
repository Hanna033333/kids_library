"""
Threads 발행 관련 FastAPI 라우터.

비즈니스 로직은 services/ 모듈로 분리되어 있으며,
이 파일은 HTTP 엔드포인트와 오케스트레이션만 담당합니다.

  services/ai_content.py   — Gemini 콘텐츠 생성
  services/text_trimmer.py — 텍스트 트리밍 유틸
  services/scheduler.py    — 주간 스케줄러
"""

import os
import uuid
import datetime
import asyncio
from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx

from core.config import THREADS_ACCESS_TOKEN, THREADS_USER_ID
from core.taxonomy import get_weekly_curations
from core.database import supabase
from services.card_generator import generate_card_news
from services.threads_publisher import upload_image_to_supabase, publish_carousel_to_threads
from services.telegram_notifier import send_threads_preview, send_threads_text_preview, send_telegram_message
from services.ai_content import generate_ai_threads_content, apply_feedback_with_gemini
from services.scheduler import weekly_threads_scheduler

router = APIRouter(prefix="/api/threads", tags=["threads"])

# 관리자 인증 토큰 (보안 적용)
THREADS_ADMIN_TOKEN = os.getenv("THREADS_ADMIN_TOKEN", "checkjari_threads_admin_2026")


# ─── Pydantic 모델 ────────────────────────────────────────────────────────────

class ThreadsTriggerRequest(BaseModel):
    curation_tag: Optional[str] = None
    curation_title: Optional[str] = None
    age_group: Optional[str] = None


class WeeklyTriggerRequest(BaseModel):
    index: Optional[int] = None


# ─── 내부 헬퍼 ───────────────────────────────────────────────────────────────

def _resolve_backend_url() -> str:
    """BACKEND_URL 환경변수를 읽어 로컬 루프백 주소를 lvh.me로 치환하여 반환합니다."""
    url = os.getenv("BACKEND_URL", "http://lvh.me:8000")
    return url.replace("localhost", "lvh.me").replace("127.0.0.1", "lvh.me")


def select_five_books(curation_tag: str) -> List[dict]:
    """도서 데이터베이스에서 조건에 맞는 책 5권을 엄선합니다. (ㄱㄴㄷ 정렬 적용)"""
    query = supabase.table("childbook_items").select("*")
    query = query.or_("is_hidden.is.null,is_hidden.eq.false")
    query = query.not_.is_("image_url", "null")
    query = query.neq("image_url", "")
    query = query.ilike("curation_tag", f"%{curation_tag}%")
    query = query.order("title")
    result = query.execute()
    books = result.data if result.data else []

    if len(books) < 5:
        needed = 5 - len(books)
        fb = supabase.table("childbook_items").select("*")
        fb = fb.or_("is_hidden.is.null,is_hidden.eq.false")
        fb = fb.not_.is_("image_url", "null")
        fb = fb.neq("image_url", "")
        if books:
            fb = fb.not_.in_("id", [b["id"] for b in books])
        fb = fb.order("title").limit(needed)
        fb_result = fb.execute()
        if fb_result.data:
            books.extend(fb_result.data)

    return books[:5]


async def execute_weekly_threads_generation(
    index: int,
    curation_tag: Optional[str] = None,
    curation_title: Optional[str] = None,
) -> int:
    """지정된 주간 큐레이션 인덱스를 사용해 도서 선정 → 텍스트 시안 생성 → 텔레그램 전송을 수행합니다."""
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    now_date = datetime.datetime.now(tz_kst).date()

    curations = get_weekly_curations(now_date)
    if not curations or index >= len(curations):
        raise ValueError(f"해당 인덱스({index})의 주간 큐레이션이 존재하지 않습니다.")

    curation = curations[index]
    c_tag = curation_tag or curation["tag"]
    c_title = curation_title or curation["title"]

    print(f"📚 [스레드 발행 파이프라인] 테마: '{c_title}' (태그: '{c_tag}') 작업 시작")

    books = select_five_books(c_tag)
    if len(books) < 5:
        raise ValueError("큐레이션 도서가 부족합니다. 최소 5권의 도서가 필요합니다.")

    ai_content = generate_ai_threads_content(c_title, c_tag, books)

    db_result = supabase.table("threads_feeds").insert({
        "title": c_title,
        "content": ai_content["caption"],
        "curation_tag": c_tag,
        "book_ids": [b["id"] for b in books],
        "card_descriptions": ai_content["card_descriptions"],
        "is_approved": False,
    }).execute()

    if not db_result.data:
        raise RuntimeError("Supabase에 피드 데이터를 삽입하는 데 실패했습니다.")

    feed_id = db_result.data[0]["id"]
    backend_url = _resolve_backend_url()
    confirm_url = f"{backend_url}/api/threads/approve-text?feed_id={feed_id}"

    books_list = [
        {
            "title": b.get("title", "제목"),
            "publisher": b.get("publisher", "출판사"),
            "description": ai_content["card_descriptions"][idx] if idx < len(ai_content["card_descriptions"]) else "",
        }
        for idx, b in enumerate(books)
    ]

    await send_threads_text_preview(
        caption=ai_content["caption"],
        books=books_list,
        confirm_url=confirm_url,
    )
    print(f"✅ [스레드 발행 파이프라인] 1단계 텍스트 시안 텔레그램 전송 완료. Feed ID: {feed_id}")
    return feed_id


async def process_telegram_feedback(feedback_text: str):
    """텔레그램 방에 보낸 피드백 텍스트를 기반으로 오늘자 미승인 피드를 수정하여 재생성합니다."""
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    today_str = datetime.datetime.now(tz_kst).strftime("%Y-%m-%d")

    db_result = (
        supabase.table("threads_feeds")
        .select("*")
        .eq("is_approved", False)
        .gte("created_at", f"{today_str}T00:00:00+09:00")
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

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
        books=books,
    )

    if not new_content:
        await send_telegram_message("❌ AI 수정 중 오류가 발생했습니다. 다시 시도해 주세요.")
        return

    supabase.table("threads_feeds").update({
        "content": new_content["caption"],
        "card_descriptions": new_content["card_descriptions"],
    }).eq("id", feed_id).execute()

    backend_url = _resolve_backend_url()
    confirm_url = f"{backend_url}/api/threads/approve-text?feed_id={feed_id}"

    books_list = [
        {
            "title": b.get("title", "제목"),
            "publisher": b.get("publisher", "출판사"),
            "description": new_content["card_descriptions"][idx] if idx < len(new_content["card_descriptions"]) else "",
        }
        for idx, b in enumerate(books)
    ]

    await send_telegram_message("✨ <b>수정이 완료되었습니다. 아래 새로운 시안을 확인해 주세요.</b>")
    await send_threads_text_preview(caption=new_content["caption"], books=books_list, confirm_url=confirm_url)


async def telegram_feedback_listener():
    """텔레그램 getUpdates API를 주기적으로 풀링하여 사용자 피드백을 감지하고 반영합니다."""
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
            try:
                params = {"timeout": 10}
                if offset is not None:
                    params["offset"] = offset

                response = await client.get(f"{api_base}/getUpdates", params=params, timeout=15.0)
                if response.status_code == 200:
                    res_json = response.json()
                    if res_json.get("ok"):
                        for update in res_json.get("result", []):
                            update_id = update["update_id"]
                            offset = update_id + 1

                            message = update.get("message")
                            if not message:
                                continue

                            text = message.get("text")
                            from_chat_id = str(message.get("chat", {}).get("id"))

                            if text and from_chat_id == chat_id and not text.startswith("/"):
                                print(f"💬 [Telegram Feedback] 사용자 피드백 감지: '{text}'")
                                await process_telegram_feedback(text)
            except Exception as e:
                print(f"❌ [Telegram Feedback Listener] 에러 발생: {e}")

            await asyncio.sleep(3)


# ─── 시작 시 스케줄러 등록용 래퍼 ────────────────────────────────────────────

async def start_weekly_scheduler():
    """main.py startup_event에서 호출하는 스케줄러 진입점."""
    await weekly_threads_scheduler(execute_fn=execute_weekly_threads_generation)


# ─── FastAPI 라우터 엔드포인트 ────────────────────────────────────────────────

def _resolve_weekday_index(weekday: int) -> int:
    if weekday == 0:
        return 0
    elif weekday == 2:
        return 1
    elif weekday == 4:
        return 2
    return 0


@router.get("/trigger-weekly")
async def trigger_weekly_get(
    index: Optional[int] = Query(None, description="주간 큐레이션 인덱스 (0: 월, 1: 수, 2: 금)"),
    curation_tag: Optional[str] = Query(None, description="커스텀 큐레이션 태그"),
    curation_title: Optional[str] = Query(None, description="커스텀 큐레이션 타이틀"),
):
    """수동으로 1단계 텍스트 시안 및 이미지 생성 요청을 텔레그램으로 보냅니다."""
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    now_kst = datetime.datetime.now(tz_kst)
    target_idx = index if index is not None else _resolve_weekday_index(now_kst.weekday())

    try:
        feed_id = await execute_weekly_threads_generation(
            index=target_idx,
            curation_tag=curation_tag,
            curation_title=curation_title,
        )
        return {"status": "success", "message": "1단계 텍스트 시안 발송 완료", "feed_id": feed_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-weekly")
async def trigger_weekly_post(req: WeeklyTriggerRequest):
    """수동으로 1단계 텍스트 시안 및 이미지 생성 요청을 텔레그램으로 보냅니다. (POST 호출 대응)"""
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    now_kst = datetime.datetime.now(tz_kst)
    target_idx = req.index if req.index is not None else _resolve_weekday_index(now_kst.weekday())

    try:
        feed_id = await execute_weekly_threads_generation(index=target_idx)
        return {"status": "success", "message": "1단계 텍스트 시안 발송 완료", "feed_id": feed_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approve-text", response_class=HTMLResponse)
async def approve_text(feed_id: int):
    """1단계 승인 처리: 실제 카드뉴스 이미지를 렌더링하고 업로드하여 2단계 검수 요청을 텔레그램으로 발송합니다."""
    feed_result = supabase.table("threads_feeds").select("*").eq("id", feed_id).execute()
    if not feed_result.data:
        raise HTTPException(status_code=404, detail="해당 피드 레코드를 찾을 수 없습니다.")

    feed = feed_result.data[0]
    book_ids = feed["book_ids"]
    curation_title = feed["title"]
    caption = feed["content"]
    card_descriptions = feed.get("card_descriptions", []) or []

    books_data = supabase.table("childbook_items").select("*").in_("id", book_ids).execute().data or []
    id_map = {b["id"]: b for b in books_data}
    books = [id_map[bid] for bid in book_ids if bid in id_map]

    await send_telegram_message("🎨 <b>카드뉴스 이미지 생성 및 Supabase Storage 업로드를 시작합니다. 약 10~20초 소요됩니다...</b>")

    image_urls = []
    for idx, b in enumerate(books):
        desc = card_descriptions[idx] if idx < len(card_descriptions) else ""
        card_img = generate_card_news(
            title=b.get("title", "제목"),
            author="",
            publisher=b.get("publisher", "출판사"),
            cover_url=b.get("image_url", ""),
            description=desc,
            curation_title=curation_title,
        )
        file_name = f"threads_feeds/{feed_id}/{uuid.uuid4()}.png"
        public_url = await upload_image_to_supabase(card_img, file_name)
        image_urls.append(public_url)

    supabase.table("threads_feeds").update({"image_urls": image_urls}).eq("id", feed_id).execute()

    backend_url = _resolve_backend_url()
    confirm_url = f"{backend_url}/api/threads/approve?feed_id={feed_id}"
    await send_threads_preview(caption=caption, image_urls=image_urls, confirm_url=confirm_url)

    return HTMLResponse(content=_html_card_generated(), status_code=200)


@router.get("/approve", response_class=HTMLResponse)
async def approve_threads_feed(feed_id: int):
    """2단계 최종 승인 처리: 발행 예약 활성화 처리 및 텔레그램 완료 알림 발송"""
    db_result = supabase.table("threads_feeds").update({"is_approved": True}).eq("id", feed_id).execute()
    if not db_result.data:
        raise HTTPException(status_code=404, detail="해당 피드 레코드를 찾을 수 없습니다.")

    await send_telegram_message("🚀 <b>주간 큐레이션 발행 승인이 최종 완료되었습니다!</b> 오늘 저녁 8시 정규 스케줄에 자동으로 Threads로 최종 발행됩니다.")
    return HTMLResponse(content=_html_approve_complete(), status_code=200)


@router.get("/debug-telegram")
async def debug_telegram():
    """텔레그램 봇 연동 상태 및 메시지 발송 기능을 검증합니다."""
    import httpx as _httpx
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
    async with _httpx.AsyncClient() as client:
        try:
            me_data = (await client.get(f"{api_base}/getMe", timeout=5.0)).json()
            msg_data = (await client.post(f"{api_base}/sendMessage", json={"chat_id": chat_id, "text": "🛠️ [Render 상용 서버 디버그] 텔레그램 메시지 발송 테스트 성공!"}, timeout=5.0)).json()
            confirm_url = f"{backend_url or 'http://lvh.me:8000'}/api/threads/approve-text?feed_id=test"
            btn_data = (await client.post(f"{api_base}/sendMessage", json={"chat_id": chat_id, "text": f"🛠️ [Render 상용 서버 디버그] 인라인 버튼 전송 테스트\nURL: {confirm_url}", "reply_markup": {"inline_keyboard": [[{"text": "테스트 승인", "url": confirm_url}]]}}, timeout=5.0)).json()
            return {"status": "success", "details": status_info, "getMe": me_data, "sendMessage_simple": msg_data, "sendMessage_button": btn_data}
        except Exception as e:
            return {"status": "error", "message": str(e), "details": status_info}


# ─── HTML 응답 헬퍼 ───────────────────────────────────────────────────────────

def _base_html(icon: str, title: str, body: str, cta: str, cta_color: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>책자리 관리자 - {title}</title>
  <style>
    body {{ font-family: 'SUIT', sans-serif; background-color: #F5F5F8; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
    .card {{ background-color: #fff; padding: 40px; border-radius: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.06); text-align: center; max-width: 480px; width: 100%; }}
    .icon {{ font-size: 48px; margin-bottom: 20px; }}
    h1 {{ color: #111827; font-size: 24px; margin-bottom: 12px; font-weight: 700; }}
    p {{ color: #6B7280; font-size: 15px; line-height: 1.6; margin-bottom: 30px; }}
    .btn {{ background-color: {cta_color}; color: {"#fff" if cta_color == "#F59E0B" else "#F59E0B"}; padding: 14px 24px; border-radius: 12px; font-weight: 700; display: inline-block; border: none; {"text-decoration: none;" if cta_color == "#F59E0B" else ""} }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">{icon}</div>
    <h1>{title}</h1>
    <p>{body}</p>
    <div class="btn">{cta}</div>
  </div>
</body>
</html>"""


def _html_card_generated() -> str:
    return _base_html(
        icon="🎨",
        title="카드뉴스 이미지 생성 완료",
        body="선택하신 도서들의 카드뉴스 비주얼 이미지 5장이 성공적으로 생성 및 업로드되었습니다.<br>텔레그램 방에 전송된 최종 이미지 시안을 확인하신 후, 발행 예약을 확정해 주세요!",
        cta="텔레그램 2차 검수 확인 대기 중...",
        cta_color="#FDE68A",
    )


def _html_approve_complete() -> str:
    return _base_html(
        icon="🚀",
        title="최종 발행 예약 완료",
        body="주간 큐레이션의 Threads 최종 발행 예약이 완료되었습니다.<br>지정된 정규 스케줄 시각(저녁 8시)에 스레드로 자동 발행됩니다.",
        cta="발행 대기 중",
        cta_color="#F59E0B",
    )