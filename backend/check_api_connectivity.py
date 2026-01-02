import os
import requests
import asyncio
import aiohttp
from core.config import DATA4LIBRARY_KEY

# 판교 도서관 코드
PANGYO_LIB_CODE = "141231"

def check_env():
    print(f"DATA4LIBRARY_KEY exists: {bool(DATA4LIBRARY_KEY)}")
    if DATA4LIBRARY_KEY:
        print(f"Key length: {len(DATA4LIBRARY_KEY)}")
        print(f"Key preview: {DATA4LIBRARY_KEY[:5]}...")

async def check_api():
    print("\nChecking Data4Library API...")
    url = "http://data4library.kr/api/bookExist"
    # 테스트용 ISBN (알라딘 API에서 가져온 것 등)
    # 예: 해리포터 등 흔한 책
    test_isbn = "9788983920678" 
    
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "isbn13": test_isbn,
        "format": "json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            start_time = asyncio.get_event_loop().time()
            async with session.get(url, params=params, timeout=10) as response:
                duration = asyncio.get_event_loop().time() - start_time
                print(f"Status Code: {response.status}")
                print(f"Duration: {duration:.2f}s")
                
                if response.status == 200:
                    text = await response.text()
                    print(f"Response Body Preview: {text[:200]}")
                    try:
                        data = await response.json()
                        result = data.get("response", {}).get("result", {})
                        print(f"Result: {result}")
                    except:
                        print("Failed to parse JSON")
                else:
                    print("API Request Failed")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_env()
    asyncio.run(check_api())
