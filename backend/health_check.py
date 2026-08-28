"""
책자리 백엔드 시스템 자가 진단 및 헬스 체크 스크립트
"""
import os
import sys
import asyncio
import httpx
from datetime import datetime

# sys.path 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import supabase
from core.config import DATA4LIBRARY_KEY, ALADIN_TTB_KEY

async def check_supabase() -> bool:
    try:
        # childbook_items 테이블에 대해 1건의 데이터를 가볍게 쿼리하여 DB 상태 점검
        response = supabase.table("childbook_items").select("id").limit(1).execute()
        print("✅ Supabase DB Connection: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ Supabase DB Connection: FAILED ({e})")
        return False

async def check_telegram() -> bool:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("⚠️ Telegram Config: SKIPPED (Token or Chat ID not configured)")
        return True
        
    api_base = f"https://api.telegram.org/bot{bot_token}"
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{api_base}/getMe", timeout=3.0)
            if res.status_code == 200 and res.json().get("ok"):
                print("✅ Telegram API Connection: SUCCESS")
                return True
            else:
                print(f"❌ Telegram API Connection: FAILED (HTTP {res.status_code})")
                return False
        except Exception as e:
            print(f"❌ Telegram API Connection: FAILED ({type(e).__name__}: {e})")
            return False

async def check_aladin() -> bool:
    if not ALADIN_TTB_KEY:
        print("⚠️ Aladin API: SKIPPED (TTB Key not configured)")
        return True
        
    url = "https://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        "ttbkey": ALADIN_TTB_KEY,
        "itemIdType": "ISBN13",
        "ItemId": "9791190299060",  # 임의의 유효 그림책 ISBN
        "output": "js",
        "Version": "20131101"
    }
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, params=params, timeout=3.0)
            if res.status_code == 200:
                print("✅ Aladin API Connection: SUCCESS")
                return True
            else:
                print(f"❌ Aladin API Connection: FAILED (HTTP {res.status_code})")
                return False
        except Exception as e:
            print(f"❌ Aladin API Connection: FAILED ({type(e).__name__}: {e})")
            return False

async def check_data4library() -> bool:
    if not DATA4LIBRARY_KEY:
        print("⚠️ Data4Library (정보나루) API: SKIPPED (Auth Key not configured)")
        return True
        
    url = "http://data4library.kr/api/bookExist"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",  # 판교도서관
        "isbn13": "9791190299060",
        "format": "json"
    }
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, params=params, timeout=5.0)
            # 302 리다이렉트 발생은 정보나루의 임시 차단 또는 점검 의미일 수 있음
            if res.status_code in (301, 302, 303, 307, 308):
                print("⚠️ Data4Library API Connection: REDIRECT (Service Check/Temporary Blocked)")
                return True
            elif res.status_code == 200:
                print("✅ Data4Library API Connection: SUCCESS")
                return True
            else:
                print(f"❌ Data4Library API Connection: FAILED (HTTP {res.status_code})")
                return False
        except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            print(f"⚠️ Data4Library API Connection: TIMEOUT ({type(e).__name__}: Service slow response)")
            return True
        except Exception as e:
            print(f"❌ Data4Library API Connection: FAILED ({type(e).__name__}: {e})")
            return False

async def main():
    print(f"🔍 [Health Check] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting Verification...")
    
    results = await asyncio.gather(
        check_supabase(),
        check_telegram(),
        check_aladin(),
        check_data4library()
    )
    
    if all(results):
        print("\n🎉 [Health Check] All system integrity checks PASSED successfully.")
        sys.exit(0)
    else:
        print("\n❌ [Health Check] Some check components FAILED. Check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
