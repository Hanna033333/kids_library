import asyncio
import aiohttp
import os
from typing import List, Dict, Optional
from core.database import supabase
from core.config import ALADIN_TTB_KEY

async def search_aladin_isbn(session: aiohttp.ClientSession, title: str, author: str, publisher: str) -> Optional[str]:
    """
    알라딘 API를 사용하여 도서의 ISBN13을 찾습니다.
    """
    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    # 검색 정확도를 높이기 위해 제목 + 저자 + 출판사 조합 사용
    query = f"{title} {author}".strip()
    params = {
        "ttbkey": ALADIN_TTB_KEY,
        "Query": query,
        "QueryType": "Keyword",
        "MaxResults": 5,
        "start": 1,
        "SearchTarget": "Book",
        "output": "js",
        "Version": "20131101"
    }
    
    try:
        async with session.get(url, params=params, timeout=10) as response:
            if response.status != 200:
                return None
            
            data = await response.json()
            items = data.get("item", [])
            
            if not items:
                # 제목 + 저자로 검색 실패 시 제목만으로 재시도
                params["Query"] = title
                async with session.get(url, params=params, timeout=10) as response2:
                    if response2.status == 200:
                        data = await response2.json()
                        items = data.get("item", [])

            if not items:
                return None
            
            # 검색 결과 중 제목이 가장 유사한 것 선택 (보통 첫 번째 결과)
            # 여기서는 첫 번째 아이템의 isbn13 반환
            for item in items:
                isbn13 = item.get("isbn13")
                if isbn13 and len(isbn13) == 13 and not isbn13.endswith("000000"):
                    return isbn13
            
            return None
    except Exception as e:
        print(f"Aladin Search Error for '{title}': {e}")
        return None

async def restore_isbns():
    print("ISBN 복구 작업을 시작합니다 (Aladin API 사용)...")
    
    # 1. 대상 도서 불러오기 (ISBN이 오염된 경우: 끝이 000000 으로 끝나는 도서들)
    try:
        # Supabase에서는 SQL LIKE 연산자가 없으므로 전체 불러온 후 필터링하거나 
        # 혹은 no_callno의 모든 책을 대상으로 확인
        response = supabase.table("no_callno").select("*").execute()
        books = response.data
        if not books:
            print("처리할 도서가 없습니다.")
            return
        
        # 실제 복구가 필요한 도서만 필터링 (ISBN이 0으로 끝남)
        # books_to_fix = [b for b in books if str(b.get("isbn", "")).endswith("000000")]
        # 모든 도서에 대해 정확한 ISBN 확인 (사용자 요청에 따라)
        books_to_fix = books
        print(f"전체 {len(books)}권 중 복구 시도 대상: {len(books_to_fix)}권")
        
    except Exception as e:
        print(f"DB Fetch Error: {e}")
        return

    # 2. 알라딘 검색 및 업데이트
    semaphore = asyncio.Semaphore(5) # API 속도 제한 고려
    
    async def process_book(session, book):
        async with semaphore:
            title = book.get("title", "")
            author = book.get("author", "")
            publisher = book.get("publisher", "")
            
            new_isbn = await search_aladin_isbn(session, title, author, publisher)
            
            if new_isbn:
                try:
                    supabase.table("no_callno").update({"isbn": new_isbn}).eq("id", book["id"]).execute()
                    print(f"[Restored] '{title}' -> {new_isbn}")
                    return True
                except Exception as e:
                    print(f"Update Error for '{title}': {e}")
            else:
                print(f"[Failed] Could not find ISBN for '{title}'")
            return False

    async with aiohttp.ClientSession() as session:
        tasks = [process_book(session, book) for book in books_to_fix]
        results = await asyncio.gather(*tasks)
        
    success_count = sum(1 for r in results if r)
    print(f"\nISBN 복구 완료: {success_count}/{len(books_to_fix)} 성공")

if __name__ == "__main__":
    asyncio.run(restore_isbns())
