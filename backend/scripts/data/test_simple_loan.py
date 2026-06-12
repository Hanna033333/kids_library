"""간단한 API 테스트 - 한 권만"""
import asyncio
import aiohttp
import sys
import json
sys.path.insert(0, '.')

from core.config import DATA4LIBRARY_KEY

async def test_one_book():
    # 알려진 ISBN으로 테스트 (곰 사냥을 떠나자)
    isbn = "9788931005158"
    lib_code = "141231"
    
    print(f"테스트 ISBN: {isbn}")
    print(f"도서관 코드: {lib_code}")
    print(f"API 키: {DATA4LIBRARY_KEY[:10]}...")
    print()
    
    url = "http://data4library.kr/api/bookExist"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": lib_code,
        "isbn13": isbn,
        "format": "json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=5) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print("\nFull Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            result = data.get("response", {}).get("result", {})
            print(f"\nhasBook: {result.get('hasBook')}")
            print(f"loanAvailable: {result.get('loanAvailable')}")

asyncio.run(test_one_book())
