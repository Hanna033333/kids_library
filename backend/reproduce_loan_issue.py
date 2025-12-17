import asyncio
import aiohttp
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"
TEST_ISBN = "9791192372754" # 아까 itemSrch 결과에 있었던 valid ISBN

async def test_book_exist():
    url = "http://data4library.kr/api/bookExist"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "isbn13": TEST_ISBN,
        "format": "json"
    }
    
    print(f"Testing bookExist for ISBN {TEST_ISBN}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                print(f"Status Code: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {data}")
                else:
                    print("Error: Status not 200")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_book_exist())
