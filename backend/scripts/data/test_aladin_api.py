"""
알라딘 API 테스트
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# 환경변수 로딩 (보안: 하드코딩 제거)
load_dotenv()
ALADIN_TTB_KEY = os.getenv("ALADIN_TTB_KEY")

if not ALADIN_TTB_KEY:
    print("❌ Error: ALADIN_TTB_KEY not found in .env file")
    exit(1)

async def test_aladin(isbn):
    url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        "ttbkey": ALADIN_TTB_KEY,
        "itemIdType": "ISBN13" if len(isbn) == 13 else "ISBN",
        "ItemId": isbn,
        "output": "js",
        "Version": "20131101",
        "OptResult": "description"
    }
    
    print(f"ISBN: {isbn}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print("="*60)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"\n응답 키들: {data.keys()}")
                    
                    if "item" in data and len(data["item"]) > 0:
                        item = data["item"][0]
                        desc = item.get("description", "")
                        print(f"\n책 소개 길이: {len(desc)} 글자")
                        print(f"\n책 소개 (처음 200자):\n{desc[:200]}")
                        return desc
                    else:
                        print("\n❌ item 없음")
                        return None
                else:
                    print(f"\n❌ HTTP {response.status}")
                    return None
    except Exception as e:
        print(f"\n❌ 에러: {e}")
        return None

async def main():
    from supabase_client import supabase
    
    # 겨울방학 책 중 ISBN이 있는 것 3권 가져오기
    result = supabase.table('childbook_items').select(
        'title,isbn'
    ).eq('curation_tag', '겨울방학2026').not_.is_('isbn', 'null').limit(3).execute()
    
    for book in result.data:
        print(f"\n{'='*60}")
        print(f"제목: {book['title']}")
        desc = await test_aladin(book['isbn'])
        if desc:
            print(f"✅ 성공")
        else:
            print(f"❌ 실패")
        print("="*60)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
