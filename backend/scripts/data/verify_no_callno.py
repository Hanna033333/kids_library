import asyncio
import aiohttp
import os
from typing import List, Dict, Optional
from core.database import supabase
from core.config import DATA4LIBRARY_KEY

# 판교 도서관 코드
PANGYO_LIB_CODE = "141231"

async def fetch_item_details_detail(session: aiohttp.ClientSession, isbn: str = None, title: str = None, author: str = None) -> Optional[Dict]:
    """
    srchDtlList API를 사용하여 도서의 상세 정보를 조회합니다.
    itemSrch보다 더 정확한 검색이 가능합니다.
    """
    url = "http://data4library.kr/api/srchDtlList"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "format": "json",
        "pageNo": 1,
        "pageSize": 5
    }
    
    if isbn:
        params["isbn13"] = isbn
    elif title:
        params["title"] = title
        if author:
            # 저자명에서 앞부분만 사용 (정확도 확보)
            params["author"] = author.split('|')[0].split('(')[0].strip()
    
    try:
        async with session.get(url, params=params, timeout=10) as response:
            if response.status != 200:
                print(f"API Error: {response.status} for {isbn or title}")
                return None
            
            data = await response.json()
            docs = data.get("response", {}).get("docs", [])
            
            if not docs:
                return None
            
            # 검색 결과 검증 (제목이 어느 정도 일치해야 함)
            doc = docs[0].get("doc", {})
            result_title = doc.get("bookname", "")
            
            # 키워드 검색인 경우 제목 검증 강화
            if title and title not in result_title and result_title not in title:
                # 제목이 너무 다르면 (ex: 대항해시대...) 무시
                print(f"Title mismatch: Expected '{title}', Got '{result_title}'")
                return None
            
            class_no = doc.get("class_no", "")
            call_numbers = doc.get("callNumbers", [])
            
            if call_numbers:
                cn = call_numbers[0].get("callNumber", {})
                sep_code = cn.get("separate_shelf_code", "")
                book_code = cn.get("book_code", "")
                
                full_callno = ""
                if sep_code:
                    full_callno += f"{sep_code} "
                if class_no:
                    full_callno += f"{class_no}"
                if book_code:
                    full_callno += f"-{book_code}"
                
                return {
                    "callno": full_callno.strip(),
                    "title": result_title
                }
            
            return None
    except Exception as e:
        print(f"Error fetching details for {isbn or title}: {e}")
        return None

async def verify_book(session: aiohttp.ClientSession, book: Dict):
    """
    단일 도서에 대해 2단계 검증을 수행합니다 (srchDtlList 사용).
    """
    isbn = str(book.get("isbn", ""))
    title = book.get("title", "")
    author = book.get("author", "")
    book_id = book.get("id")
    
    real_status = "미소장"
    real_callno = None
    isbn_callno = None
    
    # --- 1단계: ISBN 상세 검색 ---
    if isbn and not isbn.endswith("000000"):
        found = await fetch_item_details_detail(session, isbn=isbn)
        if found:
            real_status = "소장"
            real_callno = found["callno"]
            isbn_callno = found["callno"]
            print(f"[Success] Stage 1 (ISBN) - '{title}' -> {real_callno}")
        else:
            isbn_callno = "null"
            print(f"[Fail] Stage 1 (ISBN) - '{title}' ({isbn})")
    else:
        isbn_callno = "null"
        print(f"[Skip] Stage 1 (Invalid ISBN) - '{title}'")
    
    # --- 2단계: 제목/저자 상세 검색 (1단계 실패 시) ---
    if real_status == "미소장":
        found = await fetch_item_details_detail(session, title=title, author=author)
        if found:
            real_status = "소장"
            real_callno = found["callno"]
            print(f"[Success] Stage 2 (Title/Author) - '{title}' -> {real_callno}")
        else:
            print(f"[Final Fail] - '{title}'")
                
    # --- DB 업데이트 ---
    try:
        update_data = {
            "real_status": real_status,
            "real_callno": real_callno,
            "isbn_callno": isbn_callno
        }
        supabase.table("no_callno").update(update_data).eq("id", book_id).execute()
    except Exception as e:
        print(f"DB Update Error for '{title}': {e}")

async def main():
    print("no_callno 테이블 데이터 재검증을 시작합니다 (srchDtlList 사용)...")
    
    try:
        response = supabase.table("no_callno").select("*").execute()
        books = response.data
        if not books:
            print("처리할 데이터가 없습니다.")
            return
        print(f"총 {len(books)}권의 도서를 검증합니다.")
    except Exception as e:
        print(f"DB Fetch Error: {e}")
        return

    semaphore = asyncio.Semaphore(5)
    
    async def sem_verify(session, book):
        async with semaphore:
            await verify_book(session, book)

    async with aiohttp.ClientSession() as session:
        tasks = [sem_verify(session, book) for book in books]
        await asyncio.gather(*tasks)
        
    print("\n모든 검증 및 업데이트 작업이 완료되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
