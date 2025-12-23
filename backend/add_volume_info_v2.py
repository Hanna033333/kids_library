#!/usr/bin/env python
"""
중복된 청구기호를 가진 책들에 권차정보 추가 (개선 버전)
itemSrch API를 사용하여 청구기호로 검색 후 ISBN 매칭
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional
from collections import defaultdict
from supabase_client import supabase
from core.config import DATA4LIBRARY_KEY

# 판교 도서관 코드
PANGYO_LIB_CODE = "141231"

async def fetch_books_by_callno(session: aiohttp.ClientSession, callno: str) -> Optional[List[Dict]]:
    """청구기호로 도서관 장서 검색"""
    url = "http://data4library.kr/api/itemSrch"
    
    # 청구기호에서 '아' 같은 구분기호 제거하고 검색
    search_keyword = callno.replace("아 ", "").replace("유 ", "").strip()
    
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "callNumber",  # 청구기호로 검색
        "keyword": search_keyword,
        "startDt": "2000-01-01",
        "endDt": "2025-12-31",
        "pageNo": 1,
        "pageSize": 100,
        "format": "json"
    }
    
    for attempt in range(3):  # 3번 재시도
        try:
            async with session.get(url, params=params, timeout=60) as response:
                if response.status != 200:
                    continue
                    
                data = await response.json()
                
                # 에러 체크
                response_data = data.get("response", {})
                if "error" in response_data:
                    print(f"  ⚠️ API Error: {response_data['error']}")
                    return None
                
                # 응답 파싱
                docs = response_data.get("docs", [])
                
                # 권차정보 수집
                results = []
                for doc_wrapper in docs:
                    doc = doc_wrapper.get("doc", {})
                    isbn13 = doc.get("isbn13", "")
                    vol = doc.get("vol", "")
                    
                    if isbn13:  # ISBN이 있는 경우만
                        results.append({
                            "isbn13": isbn13,
                            "vol": vol.strip() if vol else "",
                            "bookname": doc.get("bookname", ""),
                            "class_no": doc.get("class_no", "")
                        })
                
                return results if results else None
                    
        except asyncio.TimeoutError:
            print(f"  ⚠️ 시도 {attempt+1} 타임아웃 ({callno})")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"  ⚠️ 시도 {attempt+1} 실패 ({callno}): {e}")
            await asyncio.sleep(2)
            
    return None


def find_duplicate_callnos():
    """중복된 청구기호를 가진 책들 찾기"""
    print("🔍 중복된 청구기호 검색 중...")
    
    # 모든 childbook_items 조회
    response = supabase.table("childbook_items").select("id, isbn, title, pangyo_callno").execute()
    books = response.data
    
    callno_groups = defaultdict(list)
    for book in books:
        callno = book.get("pangyo_callno")
        if callno and callno.strip():
            callno_groups[callno].append(book)
    
    duplicates = {
        callno: books_list 
        for callno, books_list in callno_groups.items() 
        if len(books_list) > 1
    }
    
    print(f"✅ {len(duplicates)}개의 중복된 청구기호 발견")
    return duplicates


async def add_volume_info_to_duplicates():
    log_file = open("volume_update_log.txt", "w", encoding="utf-8")
    def log(msg):
        print(msg)
        log_file.write(msg + "\n")
        
    log("\n" + "="*60)
    log("📚 중복 청구기호 책들에 권차정보 추가 (청구기호 검색 방식)")
    log("="*60 + "\n")
    
    duplicates = find_duplicate_callnos()
    
    if not duplicates:
        log("✅ 중복된 청구기호가 없습니다.")
        log_file.close()
        return
    
    log(f"\n📊 총 {len(duplicates)}개의 중복 청구기호 처리 예정\n")
    
    updated_count = 0
    not_found_count = 0
    
    async with aiohttp.ClientSession() as session:
        for idx, (callno, books_list) in enumerate(duplicates.items(), 1):
            log(f"\n[{idx}/{len(duplicates)}] 📂 청구기호: {callno}")
            log(f"  책 개수: {len(books_list)}")
            
            # 청구기호로 API 검색
            api_results = await fetch_books_by_callno(session, callno)
            
            if not api_results:
                log(f"  ❌ API에서 결과를 찾을 수 없음")
                not_found_count += len(books_list)
                for book in books_list:
                    log(f"    - {book['title'][:30]}... (ISBN: {book.get('isbn', 'N/A')})")
                await asyncio.sleep(1.5)  # API 부하 방지
                continue
            
            log(f"  ✅ API에서 {len(api_results)}개 결과 발견")
            
            # ISBN으로 매칭
            isbn_to_vol = {item["isbn13"]: item["vol"] for item in api_results}
            
            for book in books_list:
                isbn = book.get("isbn", "")
                title = book.get("title", "")[:30]
                
                if isbn in isbn_to_vol:
                    vol = isbn_to_vol[isbn]
                    if vol:  # vol이 비어있지 않은 경우만 업데이트
                        try:
                            supabase.table("childbook_items").update({"vol": vol}).eq("id", book["id"]).execute()
                            log(f"    ✅ {title}... → vol '{vol}'")
                            updated_count += 1
                        except Exception as e:
                            log(f"    ❌ 업데이트 실패: {e}")
                    else:
                        log(f"    💨 {title}... → vol 정보 없음")
                else:
                    log(f"    ⚠️ {title}... → ISBN 매칭 실패")
                    not_found_count += 1
            
            log("-" * 60)
            
            # API 부하 방지
            await asyncio.sleep(1.5)
    
    log(f"\n" + "="*60)
    log(f"✅ 총 {updated_count}권 업데이트 완료")
    log(f"❌ {not_found_count}권 정보 없음")
    log("="*60)
    log_file.close()


if __name__ == "__main__":
    asyncio.run(add_volume_info_to_duplicates())
