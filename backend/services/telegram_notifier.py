import os
import html
import httpx
from typing import List

async def send_threads_preview(caption: str, image_urls: List[str], confirm_url: str) -> bool:
    """
    텔레그램 봇을 통해 카드뉴스 5장 이미지 앨범 및 최종본 캡션, 그리고 승인 링크를 전송합니다.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print(f"⚠️ TELEGRAM_BOT_TOKEN(존재여부: {bool(bot_token)}) 또는 TELEGRAM_CHAT_ID(존재여부: {bool(chat_id)})가 설정되어 있지 않아 텔레그램 미리보기 전송을 생략합니다.")
        return False

    api_base = f"https://api.telegram.org/bot{bot_token}"
    
    # 1. 5장 이미지 앨범 전송 (sendMediaGroup)
    media_group = []
    for url in image_urls[:5]:
        media_group.append({
            "type": "photo",
            "media": url
        })
        
    async with httpx.AsyncClient() as client:
        try:
            # sendMediaGroup 호출
            print("📡 [Telegram] 카드뉴스 이미지 앨범 전송 중...")
            media_response = await client.post(
                f"{api_base}/sendMediaGroup",
                json={
                    "chat_id": chat_id,
                    "media": media_group
                },
                timeout=15.0
            )
            media_result = media_response.json()
            if not media_result.get("ok"):
                print(f"❌ [Telegram] 이미지 앨범 전송 실패: {media_result}")
                
            # 2. 캡션 본문 및 승인 링크 전송 (sendMessage)
            print("📡 [Telegram] 캡션 본문 및 승인 링크 전송 중...")
            msg_text = (
                f"{caption}\n\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"📢 위 시안은 매주 월/수/금 저녁 8시 발행용 주간 큐레이션입니다.\n"
                f"시안을 확인하시고, 정규 스케줄 시각에 자동으로 Threads로 최종 배포하려면 아래 버튼을 클릭하여 승인해 주세요!"
            )
            
            message_response = await client.post(
                f"{api_base}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": msg_text,
                    "reply_markup": {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "✅ 발행 승인 완료하기",
                                    "url": confirm_url
                                }
                            ]
                        ]
                    },
                    "disable_web_page_preview": True
                },
                timeout=10.0
            )
            msg_result = message_response.json()
            if not msg_result.get("ok"):
                print(f"❌ [Telegram] 텍스트 메시지 전송 실패: {msg_result}")
                return False
                
            print("✅ [Telegram] 텔레그램 최종본 미리보기 발송 완료!")
            return True
            
        except Exception as e:
            print(f"❌ [Telegram] 미리보기 알림 전송 중 네트워크 에러 발생: {e}")
            return False

async def send_threads_text_preview(caption: str, books: List[dict], confirm_url: str) -> bool:
    """
    1단계: 텔레그램 봇을 통해 텍스트 본문(캡션) 및 카드뉴스 텍스트 시안(제목, 출판사, 설명글)과 1차 승인 버튼을 전송합니다.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("⚠️ TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되어 있지 않아 텔레그램 텍스트 미리보기 전송을 생략합니다.")
        return False

    api_base = f"https://api.telegram.org/bot{bot_token}"
    
    # 도서 시안 텍스트 빌드
    books_text = ""
    for idx, b in enumerate(books):
        title = b.get("title", "제목")
        publisher = b.get("publisher", "출판사")
        desc = b.get("description", "") or b.get("curation_note") or ""
        books_text += (
            f"📖 <b>{idx+1}. {title}</b> ({publisher})\n"
            f"└ <i>요약: {desc}</i>\n\n"
        )
        
    msg_text = (
        f"<b>[1단계: 주간 큐레이션 텍스트 시안]</b>\n\n"
        f"📝 <b>스레드 본문 캡션:</b>\n"
        f"{caption}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📚 <b>카드뉴스 개별 도서 텍스트 시안:</b>\n\n"
        f"{books_text}"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📢 텍스트 시안을 확인하신 후, 비주얼 카드뉴스 이미지 생성을 승인하시려면 아래 버튼을 눌러주세요.\n\n"
        f"💡 수정을 원하시면 이 챗방에 대화하듯 피드백 메시지를 보내주시면 AI가 즉시 자동 반영합니다."
    )
    
    async with httpx.AsyncClient() as client:
        try:
            message_response = await client.post(
                f"{api_base}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": msg_text,
                    "parse_mode": "HTML",
                    "reply_markup": {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "🎨 카드뉴스 이미지 생성 및 2차 검증하기",
                                    "url": confirm_url
                                }
                            ]
                        ]
                    },
                    "disable_web_page_preview": True
                },
                timeout=10.0
            )
            msg_result = message_response.json()
            if not msg_result.get("ok"):
                print(f"❌ [Telegram] 텍스트 시안 전송 실패: {msg_result}")
                return False
                
            print("✅ [Telegram] 텔레그램 텍스트 시안 미리보기 발송 완료!")
            return True
        except Exception as e:
            print(f"❌ [Telegram] 텍스트 시안 전송 중 에러 발생: {e}")
            return False

async def send_telegram_message(text: str) -> bool:
    """
    단순 텍스트 알림 메시지를 텔레그램으로 전송합니다.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return False
    
    api_base = f"https://api.telegram.org/bot{bot_token}"
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{api_base}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                },
                timeout=10.0
            )
            return True
        except Exception:
            return False
