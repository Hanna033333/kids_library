"""
주간 성과 리포트 API 및 매주 월요일 09:00 KST 자동 스케줄러
"""

import os
import hmac
import asyncio
import datetime
from fastapi import APIRouter, HTTPException, Query
from services.weekly_report import (
    generate_weekly_report,
    send_weekly_report_to_telegram,
    KST,
)
from services.telegram_notifier import send_telegram_message

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _verify_admin_token(token: str):
    expected = os.getenv("THREADS_ADMIN_TOKEN", "")
    if not expected or not hmac.compare_digest(token or "", expected):
        raise HTTPException(status_code=403, detail="Unauthorized admin token")


@router.get("/weekly/preview")
async def preview_weekly_report(token: str = Query(..., description="관리자 인증 토큰")):
    """텔레그램 발송 없이 주간 성과 리포트 데이터를 미리 확인합니다."""
    _verify_admin_token(token)
    return await generate_weekly_report()


@router.post("/weekly/send")
async def trigger_weekly_report(token: str = Query(..., description="관리자 인증 토큰")):
    """주간 성과 리포트를 즉시 생성하여 텔레그램으로 발송합니다."""
    _verify_admin_token(token)
    result = await send_weekly_report_to_telegram()
    return {
        "ok": result.get("telegram_sent", False),
        "period": result["period"],
        "message_html": result["message_html"],
    }


async def weekly_report_scheduler():
    """매주 월요일 오전 9시(KST)에 주간 성과 리포트를 텔레그램으로 자동 발송합니다."""
    print("⏰ [Weekly Report Scheduler] 매주 월요일 09:00 KST 스케줄러 가동 시작...")
    last_sent_date = None

    while True:
        try:
            now_kst = datetime.datetime.now(KST)
            today_date = now_kst.date()

            # 월요일(weekday == 0) 오전 9시 (09:00 ~ 09:59) 1일 1회 실행
            if now_kst.weekday() == 0 and now_kst.hour == 9:
                if last_sent_date != today_date:
                    last_sent_date = today_date
                    print(f"📊 [Weekly Report Scheduler] 월요일 09:00 감지 ({today_date}) -> 주간 리포트 발송 시작")
                    try:
                        res = await send_weekly_report_to_telegram(reference_date=today_date)
                        print(f"✅ [Weekly Report Scheduler] 발송 완료: telegram_sent={res.get('telegram_sent')}")
                    except Exception as e:
                        print(f"❌ [Weekly Report Scheduler] 리포트 발송 실패: {e}")
                        await send_telegram_message(f"❌ [주간 리포트 오류] 월요일 자동 리포트 생성 실패: {e}")
        except asyncio.CancelledError:
            print("🛑 [Weekly Report Scheduler] 태스크 종료")
            break
        except Exception as e:
            print(f"⚠️ [Weekly Report Scheduler] 루프 예외: {e}")

        await asyncio.sleep(60)
