import os
import json
import uuid
import time
import urllib.parse
import datetime
import asyncio
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai
import httpx
from PIL import Image

from core.config import GEMINI_API_KEY, THREADS_ACCESS_TOKEN, THREADS_USER_ID
from core.taxonomy import get_weekly_curations
from core.database import supabase
from services.card_generator import generate_card_news
from services.threads_publisher import upload_image_to_supabase, publish_carousel_to_threads
from services.telegram_notifier import send_threads_preview, send_threads_text_preview, send_telegram_message

router = APIRouter(prefix="/api/threads", tags=["threads"])

# 관리자 인증 토큰 (보안 적용)
THREADS_ADMIN_TOKEN = os.getenv("THREADS_ADMIN_TOKEN", "checkjari_threads_admin_2026")

class ThreadsTriggerRequest(BaseModel):
    curation_tag: Optional[str] = None
    curation_title: Optional[str] = None
    age_group: Optional[str] = None

class WeeklyTriggerRequest(BaseModel):
    index: Optional[int] = None

def select_five_books(curation_tag: str) -> List[dict]:
    """도서 데이터베이스에서 조건에 맞는 책 5권을 엄선합니다. (ㄱㄴㄷ 정렬 적용)"""
    query = supabase.table("childbook_items").select("*")
    query = query.or_("is_hidden.is.null,is_hidden.eq.false")
    query = query.not_.is_("image_url", "null")
    query = query.neq("image_url", "")
    query = query.ilike("curation_tag", f"%{curation_tag}%")
    
    # 큐레이션 기본 정렬 기준 (ㄱㄴㄷ 오름차순) 적용
    query = query.order("title")
    
    result = query.execute()
    books = result.data if result.data else []
    
    # 만약 해당 태그를 가진 도서가 5권보다 부족한 경우, 전체 도서 중에서 보충
    if len(books) < 5:
        needed = 5 - len(books)
        fallback_query = supabase.table("childbook_items").select("*")
        fallback_query = fallback_query.or_("is_hidden.is.null,is_hidden.eq.false")
        fallback_query = fallback_query.not_.is_("image_url", "null")
        fallback_query = fallback_query.neq("image_url", "")
        if books:
            book_ids = [b["id"] for b in books]
            fallback_query = fallback_query.not_.in_("id", book_ids)
        fallback_query = fallback_query.order("title").limit(needed)
        fallback_result = fallback_query.execute()
        if fallback_result.data:
            books.extend(fallback_result.data)
            
    return books[:5]

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

def _safety_trim(text: str, max_len: int = 90) -> str:
    """Gemini 생성 설명이 max_len을 초과할 경우 어절 경계에서 잘라 존댓말로 종결합니다."""
    text = text.strip()
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rfind(" ")
    result = text[:cut] if cut >= 40 else text[:max_len]
    result = result.rstrip(".")
    if not result.endswith("다"):
        result = result + " 이야기입니다."
    else:
        result = result + "."
    return result

def generate_fallback_content(curation_title: str, curation_tag: str, books: List[dict]) -> dict:
    """Gemini API 호출이 불가할 때 로컬 DB의 도서 소개 및 요약 정보를 정제하여 스마트 폴백 텍스트를 구성합니다."""
    caption = (
        f"오늘의 추천 큐레이션은 <{curation_title}> 입니다.\n\n"
        f"우리 아이에게 꼭 맞는 책들을 엄선하여 소개해 드려요. "
        f"함께 소중한 독서 시간을 가져보는 건 어떨까요?\n\n"
        f"자세한 도서 목록과 정보는 아래 링크에서 확인해 보세요!\n"
        f"🔗 https://checkjari.com/collections/curation/{urllib.parse.quote(curation_tag)}"
    )
    
    card_descriptions = []
    for b in books:
        raw_desc = b.get("description") or b.get("curation_note") or f"{b.get('title')} 도서입니다."
        card_descriptions.append(trim_text_fallback(raw_desc))
        
    return {
        "caption": caption,
        "card_descriptions": card_descriptions
    }

def generate_ai_threads_content(curation_title: str, curation_tag: str, books: List[dict]) -> dict:
    """Gemini API를 사용하여 스레드용 캡션 및 5권 도서의 3줄 요약 설명(각 65자 내외)을 생성합니다."""
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY가 존재하지 않아 스마트 폴백 메커니즘을 작동합니다.")
        return generate_fallback_content(curation_title, curation_tag, books)
        
    genai.configure(api_key=GEMINI_API_KEY)
    
    try:
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
    except Exception:
        try:
            model = genai.GenerativeModel(
                'gemini-2.0-flash',
                generation_config={"response_mime_type": "application/json"}
            )
        except Exception as e:
            print(f"❌ GenerativeModel 생성 실패: {e}. 스마트 폴백을 작동합니다.")
            return generate_fallback_content(curation_title, curation_tag, books)
        
    books_info = []
    for idx, b in enumerate(books):
        books_info.append({
            "index": idx + 1,
            "title": b.get("title"),
            "publisher": b.get("publisher"),
            "description": b.get("description") or b.get("curation_note") or ""
        })
        
    prompt = f"""
당신은 아동 도서 전문 큐레이션 서비스 '책자리'의 AI 전문 사서입니다.
아래 도서 목록과 큐레이션 테마 정보를 바탕으로, 인스타그램 스레드(Threads)에 발행할 SNS 본문용 캡션(caption)과 각 도서 카드뉴스 이미지 내부에 들어갈 순수한 3줄짜리 책 요약 설명(card_descriptions)을 생성해 주세요.

[큐레이션 정보]
- 테마 제목: {curation_title}
- 분류 태그: {curation_tag}

[도서 목록]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 지침 - 중요]
1. 본문 캡션(caption) 작성 지침:
   - 양육자(부모님)와 깊이 공감하는 다정하고 따뜻한 존댓말 톤앤매너로 작성하세요.
   - **문단 수 엄수**: 캡션은 반드시 본문 1문단 + 링크 1줄, 총 2문단으로만 구성하세요. 문단을 3개 이상으로 늘리지 마세요.
   - 큐레이션 기획 의도와 관련된 공감되는 실제 양육 에피소드(혹은 부모로서 겪는 고민)가 캡션 첫머리에 필수적으로 배치되어야 합니다.
   - 마지막에는 서비스 유입을 위한 상세 랜딩 링크를 반드시 다음 형식으로 포함하세요:
     "🔗 https://checkjari.com/collections/curation/{{urllib.parse.quote(curation_tag)}}"
   - 맞춤법, 띄어쓰기, 문장 완성도에 오타("막맘하셨지요" 등)가 전혀 없도록 철저히 검수하세요.

2. 카드뉴스 도서 요약(card_descriptions) 작성 지침 (비주얼 가이드):
    - **글자 수 정밀 통제**: 각 도서별로 3줄을 거의 꽉 채울 수 있도록 반드시 공백 포함 60자에서 70자 사이의 완성도 있는 텍스트로 작성하세요. (글자 수가 너무 짧아지면 카드뉴스에서 2줄만 노출되어 균형이 깨지고, 70자를 초과하면 4줄이 되어 뒷부분이 잘리게 되므로, 반드시 60자~70자 범위를 맞춰 3줄을 꽉 채울 것)
    - **연결성 극대화 (뚝뚝 끊김 절대 금지)**: 명사형 종결이나 단어/구절의 단순 나열(예: "~의 일대기. ~의 삶. ~한 이야기.")을 **절대 금지**합니다. 문맥이 부드럽고 자연스럽게 한 문장 혹은 두 문장으로 유기적으로 연결된 완성형 글로 작성해 주세요.
    - **존댓말 종결 어미 필수 (반말 금지)**: 반말(예: "~그린다.", "~지켰다.", "~이야기.")로 종결되는 문장을 **엄격히 금지**합니다. 반드시 신뢰감을 주는 정중하고 부드러운 존댓말 종결 어미(예: "~이야기입니다.", "~소개해 줍니다.", "~그려내고 있습니다.", "~담고 있습니다.")만 사용하여 문장을 매끄럽게 끝맺어 주세요.
    - 양육자용 추천평 멘트(예: "부모님과 읽기 좋아요", "강력 추천합니다")는 완전히 배제하고, 순수한 책의 줄거리 요약으로만 완성도 있게 작성하세요.
    - 꼬리표 기호(예: "[줄거리 요약]", "[추천평]" 등)나 마크다운 기호는 가독성을 방해하므로 절대 포함하지 마세요.
    - 문장이 끊기거나 말줄임표(...)로 끝나서는 안 됩니다.

[반환 형식]
반드시 다음 JSON 구조로 응답해야 합니다:
{{
  "caption": "스레드 본문에 노출할 캡션 텍스트",
  "card_descriptions": [
    "1번 책의 3줄 줄거리 요약",
    "2번 책의 3줄 줄거리 요약",
    "3번 책의 3줄 줄거리 요약",
    "4번 책의 3줄 줄거리 요약",
    "5번 책의 3줄 줄거리 요약"
  ]
}}
"""

    try:
        response = model.generate_content(prompt)
        res_data = json.loads(response.text)
        if not res_data.get("caption") or len(res_data.get("card_descriptions", [])) < 5:
            raise ValueError("Invalid response structure")
        res_data["card_descriptions"] = [_safety_trim(d) for d in res_data["card_descriptions"]]
        return res_data
    except Exception as e:
        print(f"❌ Gemini API 오류 발생: {e}. 스마트 폴백 메커니즘을 작동합니다.")
        return generate_fallback_content(curation_title, curation_tag, books)

async def apply_feedback_with_gemini(
    feedback_text: str,
    old_caption: str,
    old_descriptions: List[str],
    books: List[dict]
) -> Optional[dict]:
    """Gemini API에 기존 텍스트 시안과 관리자의 피드백 내용을 전달하여 텍스트를 정교하게 재생성합니다."""
    if not GEMINI_API_KEY:
        return None
        
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
    except Exception:
        try:
            model = genai.GenerativeModel(
                'gemini-2.0-flash',
                generation_config={"response_mime_type": "application/json"}
            )
        except Exception:
            return None
        
    books_info = []
    for idx, b in enumerate(books):
        books_info.append({
            "index": idx + 1,
            "title": b.get("title"),
            "publisher": b.get("publisher"),
            "old_description": old_descriptions[idx] if idx < len(old_descriptions) else ""
        })
        
    prompt = f"""
당신은 아동 도서 전문 큐레이션 서비스 '책자리'의 AI 전문 사서입니다.
사용자(관리자)로부터 이전에 작성된 스레드 캡션 및 개별 도서 요약본에 대한 수정 요청(피드백)을 받았습니다.
이를 바탕으로 캡션과 각 도서의 요약을 업데이트해 주세요.

[사용자 수정 요청 (피드백)]
"{feedback_text}"

[기존 캡션]
"{old_caption}"

[기존 도서 정보 및 이전 요약]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 지침 - 중요]
1. 본문 캡션(caption) 작성 지침:
   - 사용자의 피드백을 반영하되, 양육자와 공감하는 다정하고 따뜻한 존댓말 톤앤매너를 시종일관 유지해 주세요.
   - **문단 수 엄수**: 캡션은 반드시 본문 1문단 + 링크 1줄, 총 2문단으로만 구성하세요. 문단을 3개 이상으로 늘리지 마세요.
   - 큐레이션 기획 의도와 관련된 공감되는 실제 양육 에피소드가 캡션 첫머리에 반드시 유지되어야 합니다.
   - 캡션 하단의 서비스 상세 랜딩 링크 형식을 그대로 지켜서 노출하세요. (예: 🔗 https://checkjari.com/collections/curation/...)
   - 맞춤법 및 오타가 절대 없도록 철저히 다시 보정해 주세요.

2. 카드뉴스 도서 요약(card_descriptions) 작성 지침:
    - 사용자의 피드백을 반영하여 각 도서의 3줄 요약 설명(공백 포함 60자에서 70자 사이)을 새로 정제하세요. (글자 수가 너무 짧아지면 카드뉴스에서 2줄만 노출되어 균형이 깨지고, 70자를 초과하면 4줄이 되어 뒷부분이 잘리게 되므로, 반드시 60자~70자 범위를 맞춰 3줄을 꽉 채울 것)
    - **연결성 극대화 (뚝뚝 끊김 절대 금지)**: 단어 중심의 명사형 종결이나 단절된 나열식 문장을 **절대 금지**하고, 자연스럽고 부드럽게 이어지는 **완성형 문장**들로 유기적으로 작문해 주세요.
    - **존댓말 종결 어미 필수 (반말 금지)**: 반말(예: "~그린다.", "~했다.")로 끝나는 것을 **엄격히 금지**합니다. 반드시 정중하고 격식 있는 존댓말 종결 어미(예: "~합니다.", "~입니다.", "~그려내고 있습니다.", "~소개해 줍니다.")로 마침표를 찍어 주세요.
    - 추천평 및 주관적인 형용사는 배제하고, 순수한 줄거리 요약으로만 3줄을 완성하세요.
    - 꼬리표 기호(예: "[줄거리 요약]" 등)나 마크다운 기호는 절대 넣지 마세요.
    - 말줄임표(...)로 끝나서는 안 되며 마침표로 정중히 문장을 매끄럽게 종결해 주세요.

[반환 형식]
반드시 다음 JSON 구조로 응답해야 합니다:
{{
  "caption": "수정 반영된 스레드 본문 캡션 텍스트",
  "card_descriptions": [
    "수정 반영된 1번 책의 3줄 요약",
    "수정 반영된 2번 책의 3줄 요약",
    "수정 반영된 3번 책의 3줄 요약",
    "수정 반영된 4번 책의 3줄 요약",
    "수정 반영된 5번 책의 3줄 요약"
  ]
}}
"""
    try:
        response = model.generate_content(prompt)
        res_data = json.loads(response.text)
        if not res_data.get("caption") or len(res_data.get("card_descriptions", [])) < 5:
            raise ValueError("Invalid response structure")
        res_data["card_descriptions"] = [_safety_trim(d) for d in res_data["card_descriptions"]]
        return res_data
    except Exception as e:
        print(f"❌ Gemini 피드백 수정 중 오류: {e}")
        return None

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
    
    backend_url = os.getenv("BACKEND_URL", "http://lvh.me:8000")
    if "localhost" in backend_url or "127.0.0.1" in backend_url:
        backend_url = backend_url.replace("localhost", "lvh.me").replace("127.0.0.1", "lvh.me")
        
    confirm_url = f"{backend_url}/api/threads/approve-text?feed_id={feed_id}"
    
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
    c_tag = curation_tag or curation["tag"]
    c_title = curation_title or curation["title"]
    
    print(f"📚 [스레드 발행 파이프라인] 테마: '{c_title}' (태그: '{c_tag}') 작업 시작")
    
    books = select_five_books(c_tag)
    if len(books) < 5:
        raise ValueError(f"큐레이션 도서가 부족합니다. 최소 5권의 도서가 필요합니다.")
        
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
    
    backend_url = os.getenv("BACKEND_URL", "http://lvh.me:8000")
    if "localhost" in backend_url or "127.0.0.1" in backend_url:
        backend_url = backend_url.replace("localhost", "lvh.me").replace("127.0.0.1", "lvh.me")
        
    confirm_url = f"{backend_url}/api/threads/approve-text?feed_id={feed_id}"
    
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

@router.get("/trigger-weekly")
async def trigger_weekly_get(
    index: Optional[int] = Query(None, description="주간 큐레이션 인덱스 (0: 월, 1: 수, 2: 금)"),
    curation_tag: Optional[str] = Query(None, description="커스텀 큐레이션 태그"),
    curation_title: Optional[str] = Query(None, description="커스텀 큐레이션 타이틀")
):
    """수동으로 1단계 텍스트 시안 및 이미지 생성 요청을 텔레그램으로 보냅니다."""
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
async def trigger_weekly_post(req: WeeklyTriggerRequest):
    """수동으로 1단계 텍스트 시안 및 이미지 생성 요청을 텔레그램으로 보냅니다. (POST 호출 대응)"""
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

@router.get("/approve-text", response_class=HTMLResponse)
async def approve_text(feed_id: int):
    """1단계 승인 처리: 실제 카드뉴스 이미지를 렌더링하고 업로드하여 2단계 검수 요청을 텔레그램으로 발송합니다."""
    feed_result = supabase.table("threads_feeds").select("*").eq("id", feed_id).execute()
    if not feed_result.data:
        raise HTTPException(status_code=404, detail="해당 피드 레코드를 찾을 수 없습니다.")
        
    feed = feed_result.data[0]
    book_ids = feed["book_ids"]
    curation_title = feed["title"]
    curation_tag = feed["curation_tag"]
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
        # UI-KIT 가이드에 맞춰 저자(author) 정보를 생략한 출판사 단독 노출 렌더링 진행
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
    
    backend_url = os.getenv("BACKEND_URL", "http://lvh.me:8000")
    if "localhost" in backend_url or "127.0.0.1" in backend_url:
        backend_url = backend_url.replace("localhost", "lvh.me").replace("127.0.0.1", "lvh.me")
        
    confirm_url = f"{backend_url}/api/threads/approve?feed_id={feed_id}"
    
    await send_threads_preview(
        caption=caption,
        image_urls=image_urls,
        confirm_url=confirm_url
    )
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>책자리 관리자 - 카드뉴스 이미지 생성 완료</title>
        <style>
            body {
                font-family: 'SUIT', sans-serif;
                background-color: #F5F5F8;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background-color: #FFFFFF;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.06);
                text-align: center;
                max-width: 480px;
                width: 100%;
            }
            .icon {
                font-size: 48px;
                margin-bottom: 20px;
            }
            h1 {
                color: #111827;
                font-size: 24px;
                margin-bottom: 12px;
                font-weight: 700;
            }
            p {
                color: #6B7280;
                font-size: 15px;
                line-height: 1.6;
                margin-bottom: 30px;
            }
            .status-btn {
                background-color: #FDE68A;
                color: #F59E0B;
                padding: 14px 24px;
                border-radius: 12px;
                font-weight: 700;
                display: inline-block;
                border: none;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon">🎨</div>
            <h1>카드뉴스 이미지 생성 완료</h1>
            <p>선택하신 도서들의 카드뉴스 비주얼 이미지 5장이 성공적으로 생성 및 업로드되었습니다.<br>텔레그램 방에 전송된 최종 이미지 시안을 확인하신 후, 발행 예약을 확정해 주세요!</p>
            <div class="status-btn">텔레그램 2차 검수 확인 대기 중...</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@router.get("/approve", response_class=HTMLResponse)
async def approve_threads_feed(feed_id: int):
    """2단계 최종 승인 처리: 발행 예약 활성화 처리 및 텔레그램 완료 알림 발송"""
    db_result = supabase.table("threads_feeds").update({
        "is_approved": True
    }).eq("id", feed_id).execute()
    
    if not db_result.data:
        raise HTTPException(status_code=404, detail="해당 피드 레코드를 찾을 수 없습니다.")
        
    await send_telegram_message("🚀 <b>주간 큐레이션 발행 승인이 최종 완료되었습니다!</b> 오늘 저녁 8시 정규 스케줄에 자동으로 Threads로 최종 발행됩니다.")
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>책자리 관리자 - 발행 예약 완료</title>
        <style>
            body {
                font-family: 'SUIT', sans-serif;
                background-color: #F5F5F8;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background-color: #FFFFFF;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.06);
                text-align: center;
                max-width: 480px;
                width: 100%;
            }
            .icon {
                font-size: 48px;
                margin-bottom: 20px;
            }
            h1 {
                color: #111827;
                font-size: 24px;
                margin-bottom: 12px;
                font-weight: 700;
            }
            p {
                color: #6B7280;
                font-size: 15px;
                line-height: 1.6;
                margin-bottom: 30px;
            }
            .btn {
                background-color: #F59E0B;
                color: #FFFFFF;
                padding: 14px 24px;
                border-radius: 12px;
                text-decoration: none;
                font-weight: 700;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon">🚀</div>
            <h1>최종 발행 예약 완료</h1>
            <p>주간 큐레이션의 Threads 최종 발행 예약이 완료되었습니다.<br>지정된 정규 스케줄 시각(저녁 8시)에 스레드로 자동 발행됩니다.</p>
            <div class="btn">발행 대기 중</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

async def weekly_threads_scheduler():
    """매분마다 시간을 감지하여 월/수/금 저녁 6시에는 텍스트 시안을 자동 빌드하고, 저녁 8시에는 최종 승인된 피드를 발행합니다."""
    print("⏰ [Weekly Threads Scheduler] 스케줄러 태스크 가동 시작...")
    
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    
    # 중복 실행 방지용 메모리 락 (당일 한 번만 실행)
    last_trigger_date_6pm = None
    last_trigger_date_8pm = None
    
    while True:
        try:
            now_kst = datetime.datetime.now(tz_kst)
            today_date = now_kst.date()
            weekday = now_kst.weekday()  # 0: 월, 2: 수, 4: 금
            
            # 1. 월/수/금요일 저녁 6시 (18:00) -> 1단계 텍스트 시안 생성 및 텔레그램 발송
            if weekday in (0, 2, 4) and now_kst.hour == 18 and now_kst.minute == 0:
                if last_trigger_date_6pm != today_date:
                    print(f"📡 [스케줄러] 저녁 6시 감지. 요일: {weekday}, 날짜: {today_date} -> 1단계 텍스트 시안 생성 시작")
                    target_idx = 0 if weekday == 0 else (1 if weekday == 2 else 2)
                    try:
                        # 이미 오늘 생성된 피드가 있는지 재검증
                        today_str = today_date.strftime("%Y-%m-%d")
                        dup = supabase.table("threads_feeds").select("id")\
                            .gte("created_at", f"{today_str}T00:00:00+09:00")\
                            .limit(1).execute()
                        if not dup.data:
                            await execute_weekly_threads_generation(index=target_idx)
                        last_trigger_date_6pm = today_date
                    except Exception as e:
                        print(f"❌ [스케줄러] 6시 1단계 생성 중 에러: {e}")
                        await send_telegram_message(f"❌ [스케줄러 경고] 저녁 6시 1단계 시안 생성 실패: {e}")
                        
            # 2. 월/수/금요일 저녁 8시 (20:00) -> 승인된 카드뉴스 최종 배포
            if weekday in (0, 2, 4) and now_kst.hour == 20 and now_kst.minute == 0:
                if last_trigger_date_8pm != today_date:
                    print(f"📡 [스케줄러] 저녁 8시 감지. 요일: {weekday}, 날짜: {today_date} -> 최종 배포 스캔")
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
                                print(f"📣 [스케줄러] 최종 승인된 피드({feed_id}) 배포 진행")
                                await send_telegram_message("📢 <b>[스케줄러] 최종 승인된 카드뉴스의 Threads 최종 배포를 진행합니다...</b>")
                                post_id = await publish_carousel_to_threads(text=caption, image_urls=image_urls)
                                
                                supabase.table("threads_feeds").update({
                                    "published_at": datetime.datetime.now(tz_kst).isoformat()
                                }).eq("id", feed_id).execute()
                                
                                await send_telegram_message(f"🎉 <b>[실시간 배포 완료]</b> Threads에 최종 배포되었습니다. 포스트 ID: <code>{post_id}</code>")
                            else:
                                print(f"⚠️ [스케줄러] 피드({feed_id})가 승인되었으나 이미지 URL이 존재하지 않아 배포를 생략합니다.")
                                await send_telegram_message(f"⚠️ [스케줄러 경고] 피드({feed_id})가 승인되었으나 이미지 URL이 없어 배포되지 못했습니다.")
                        else:
                            print("ℹ️ [스케줄러] 오늘 승인된 예약 발행용 피드가 발견되지 않았습니다. 발행을 건너뜁니다.")
                            await send_telegram_message("ℹ️ <b>[스케줄러 알림]</b> 오늘 저녁 8시 발행 예약 건 중 승인 완료된(Okay) 피드가 없어 발행이 생략되었습니다.")
                            
                        last_trigger_date_8pm = today_date
                    except Exception as e:
                        print(f"❌ [스케줄러] 저녁 8시 최종 배포 에러: {e}")
                        await send_telegram_message(f"❌ [스케줄러 오류] 저녁 8시 최종 발행 중 에러 발생: {e}")
                        
        except Exception as e:
            print(f"❌ [Weekly Threads Scheduler Loop Error]: {e}")
            
        await asyncio.sleep(60) # 1분 간격 체크


@router.get("/debug-telegram")
async def debug_telegram():
    import os
    import httpx
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
            confirm_url = f"{backend_url or 'http://lvh.me:8000'}/api/threads/approve-text?feed_id=test"
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