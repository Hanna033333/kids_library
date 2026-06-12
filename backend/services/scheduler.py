"""
주간 스레드 콘텐츠 스케줄러.

- 월/수/금 18:00 KST: 텍스트 시안 생성 → 텔레그램 발송
- 월/수/금 20:00 KST: 승인된 피드 Threads 최종 발행
"""

import asyncio
import datetime

from core.database import supabase
from services.telegram_notifier import send_telegram_message
from services.threads_publisher import publish_carousel_to_threads


async def weekly_threads_scheduler(execute_fn):
    """
    매분 KST 시간을 확인하여 정해진 시각에 작업을 수행합니다.

    Parameters
    ----------
    execute_fn : coroutine function
        1단계 텍스트 시안 생성 함수 (execute_weekly_threads_generation).
        순환 import 방지를 위해 주입(Dependency Injection) 방식으로 받습니다.
    """
    print("⏰ [Weekly Threads Scheduler] 스케줄러 태스크 가동 시작...")

    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    last_trigger_date_6pm = None
    last_trigger_date_8pm = None

    while True:
        try:
            now_kst = datetime.datetime.now(tz_kst)
            today_date = now_kst.date()
            weekday = now_kst.weekday()  # 0:월 2:수 4:금

            # 1. 저녁 6시 → 텍스트 시안 생성 & 텔레그램 발송
            if weekday in (0, 2, 4) and now_kst.hour == 18 and now_kst.minute == 0:
                if last_trigger_date_6pm != today_date:
                    target_idx = 0 if weekday == 0 else (1 if weekday == 2 else 2)
                    print(f"📡 [스케줄러] 저녁 6시 감지 → 인덱스 {target_idx} 시안 생성 시작")
                    try:
                        today_str = today_date.strftime("%Y-%m-%d")
                        dup = (
                            supabase.table("threads_feeds")
                            .select("id")
                            .gte("created_at", f"{today_str}T00:00:00+09:00")
                            .limit(1)
                            .execute()
                        )
                        if not dup.data:
                            await execute_fn(index=target_idx)
                        last_trigger_date_6pm = today_date
                    except Exception as e:
                        print(f"❌ [스케줄러] 6시 1단계 생성 중 에러: {e}")
                        await send_telegram_message(f"❌ [스케줄러 경고] 저녁 6시 1단계 시안 생성 실패: {e}")

            # 2. 저녁 8시 → 승인된 카드뉴스 최종 배포
            if weekday in (0, 2, 4) and now_kst.hour == 20 and now_kst.minute == 0:
                if last_trigger_date_8pm != today_date:
                    print(f"📡 [스케줄러] 저녁 8시 감지 → 최종 배포 스캔")
                    try:
                        today_str = today_date.strftime("%Y-%m-%d")
                        approved = (
                            supabase.table("threads_feeds")
                            .select("*")
                            .eq("is_approved", True)
                            .is_("published_at", "null")
                            .gte("created_at", f"{today_str}T00:00:00+09:00")
                            .order("id", desc=True)
                            .limit(1)
                            .execute()
                        )

                        if approved.data:
                            feed = approved.data[0]
                            feed_id = feed["id"]
                            caption = feed["content"]
                            image_urls = feed["image_urls"]

                            if image_urls:
                                print(f"📣 [스케줄러] 최종 승인된 피드({feed_id}) 배포 진행")
                                await send_telegram_message(
                                    "📢 <b>[스케줄러] 최종 승인된 카드뉴스의 Threads 최종 배포를 진행합니다...</b>"
                                )
                                post_id = await publish_carousel_to_threads(text=caption, image_urls=image_urls)

                                supabase.table("threads_feeds").update(
                                    {"published_at": datetime.datetime.now(tz_kst).isoformat()}
                                ).eq("id", feed_id).execute()

                                await send_telegram_message(
                                    f"🎉 <b>[실시간 배포 완료]</b> Threads에 최종 배포되었습니다. 포스트 ID: <code>{post_id}</code>"
                                )
                            else:
                                print(f"⚠️ [스케줄러] 피드({feed_id}) 이미지 URL 없음 → 배포 생략")
                                await send_telegram_message(
                                    f"⚠️ [스케줄러 경고] 피드({feed_id})가 승인되었으나 이미지 URL이 없어 배포되지 못했습니다."
                                )
                        else:
                            print("ℹ️ [스케줄러] 오늘 승인된 예약 발행용 피드 없음 → 건너뜀")
                            await send_telegram_message(
                                "ℹ️ <b>[스케줄러 알림]</b> 오늘 저녁 8시 발행 예약 건 중 승인 완료된 피드가 없어 발행이 생략되었습니다."
                            )

                        last_trigger_date_8pm = today_date
                    except Exception as e:
                        print(f"❌ [스케줄러] 저녁 8시 최종 배포 에러: {e}")
                        await send_telegram_message(f"❌ [스케줄러 오류] 저녁 8시 최종 발행 중 에러 발생: {e}")

        except Exception as e:
            print(f"❌ [Weekly Threads Scheduler Loop Error]: {e}")

        await asyncio.sleep(60)  # 1분 간격 체크
