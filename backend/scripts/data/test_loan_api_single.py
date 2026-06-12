import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_single_isbn(isbn):
    url = "http://data4library.kr/api/bookExist"
    params = {
        "authKey": os.getenv("DATA4LIBRARY_KEY"),
        "libCode": "141231",
        "isbn13": isbn,
        "format": "json"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params, timeout=10) as response:
                print(f"Status: {response.status}")
                data = await response.json()
                print("Response data:")
                import json
                print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    isbn = "9788969850386" # 빛나는 아이
    asyncio.run(test_single_isbn(isbn))
