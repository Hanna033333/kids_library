import asyncio
import aiohttp
import os
from typing import List, Dict, Set
from core.database import supabase
from core.config import DATA4LIBRARY_KEY

# 판교 도서관 코드
PANGYO_LIB_CODE = "141231"
PAGE_SIZE = 50 

async def scan_catalog(target_isbns: Set[str]):
    """
    도서관 카탈로그를 페이지단위로 스캔하여 대상 ISBN이 있는지 확인합니다.
    """
    found_map = {}
    url = "http://data4library.kr/api/itemSrch"
    
    async with aiohttp.ClientSession() as session:
        # 처음 30페이지 (30,000권) 스캔 시도
        for page in range(1, 31):
            print(f"  Scanning catalog page {page}...")
            params = {
                "authKey": DATA4LIBRARY_KEY,
                "libCode": PANGYO_LIB_CODE,
                "type": "ALL",
                "pageNo": page,
                "pageSize": PAGE_SIZE,
                "format": "json"
            }
            
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        print(f"    Page {page} failed with status {response.status}")
                        continue
                    
                    data = await response.json()
                    docs = data.get("response", {}).get("docs", [])
                    
                    if not docs:
                        print(f"    No more docs at page {page}")
                        break
                    
                    for doc_wrapper in docs:
                        doc = doc_wrapper.get("doc", {})
                        isbn13 = doc.get("isbn13")
                        if isbn13 in target_isbns:
                            # 청구기호 조합
                            class_no = doc.get("class_no", "")
                            call_numbers = doc.get("callNumbers", [])
                            if call_numbers:
                                cn = call_numbers[0].get("callNumber", {})
                                sep_code = cn.get("separate_shelf_code", "")
                                book_code = cn.get("book_code", "")
                                
                                full_callno = ""
                                if sep_code: full_callno += f"{sep_code} "
                                if class_no: full_callno += f"{class_no}"
                                if book_code: full_callno += f"-{book_code}"
                                
                                callno = full_callno.strip()
                                found_map[isbn13] = callno
                                print(f"    ✨ Found Match: '{doc.get('bookname')}' -> {callno}")
                                
            except Exception as e:
                print(f"    Error on page {page}: {e}")
                
            # 전체 다 찾았으면 중단
            if len(found_map) == len(target_isbns):
                print("    All target ISBNs found!")
                break
                
    return found_map

async def main():
    print("도서관 카탈로그 스캔을 통한 청구기호 복구를 시작합니다...")
    
    # 1. 대상 ISBN 가져오기 (아직 real_callno가 없는 것들)
    try:
        response = supabase.table("no_callno").select("id, isbn, title").is_("real_callno", "null").execute()
        books = response.data
        if not books:
            print("모든 도서의 청구기호가 이미 채워져 있습니다.")
            return
        
        target_isbns = {str(b["isbn"]) for b in books if b["isbn"]}
        print(f"대상 도서: {len(books)}권 (고유 ISBN: {len(target_isbns)}개)")
    except Exception as e:
        print(f"DB Fetch Error: {e}")
        return

    # 2. 카탈로그 스캔
    found_results = await scan_catalog(target_isbns)
    print(f"\n스캔 완료: {len(found_results)}권의 청구기호를 새로 발견했습니다.")

    # 3. DB 업데이트
    updated_count = 0
    for book in books:
        isbn = str(book["isbn"])
        if isbn in found_results:
            try:
                callno = found_results[isbn]
                supabase.table("no_callno").update({
                    "real_status": "소장",
                    "real_callno": callno,
                    "isbn_callno": callno
                }).eq("id", book["id"]).execute()
                updated_count += 1
            except Exception as e:
                print(f"Update Error for {book['title']}: {e}")
                
    print(f"DB 업데이트 완료: {updated_count}권")

if __name__ == "__main__":
    asyncio.run(main())
