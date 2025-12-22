#!/usr/bin/env python
"""
중복된 청구기호를 가진 책들에 권차정보 추가 (Refined Version 3)
- API 결과에서 ISBN/제목 엄격 대조 로직 추가
- itemSrch API 필수 파라미터 유지
- 1순위: ISBN 기반 검색
- 2순위: 제목 기반 검색 (ISBN 매칭 실패 시)
- 캐싱을 통해 동일 도서 중복 호출 방지
"""

import asyncio
import aiohttp
import re
from typing import List, Dict, Optional, Set
from collections import defaultdict
from supabase_client import supabase
from core.config import DATA4LIBRARY_KEY

# 판교 도서관 코드
PANGYO_LIB_CODE = "141231"

# API 정보
ITEM_SRCH_URL = "http://data4library.kr/api/itemSrch"

def normalize_isbn(isbn: str) -> str:
    """ISBN 정규화 (숫자만 남김)"""
    if not isbn:
        return ""
    return re.sub(r"[^0-9]", "", isbn)

def normalize_title(title: str) -> str:
    """제목 정규화 (공백, 문장부호 제거, 소문자 변환)"""
    if not title:
        return ""
    # 괄호와 그 안의 내용 제거 (예: (개정판), [전집] 등)
    title = re.sub(r"\[.*?\]", "", title)
    title = re.sub(r"\(.*?\)", "", title)
    # 특수문자 제거 및 공백 제거
    title = re.sub(r"[^a-zA-Z0-9가-힣]", "", title)
    return title.lower()

async def fetch_book_info_from_api(
    session: aiohttp.ClientSession, 
    isbn: Optional[str] = None, 
    title: Optional[str] = None
) -> List[Dict]:
    """ISBN 또는 제목으로 API 검색 수행"""
    results = []
    
    # 1. ISBN 검색 시도
    if isbn:
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": PANGYO_LIB_CODE,
            "type": "ISBN",
            "keyword": isbn,
            "startDt": "2000-01-01",
            "endDt": "2025-12-31",
            "pageNo": 1,
            "pageSize": 50, # 넉넉하게 가져옴
            "format": "json"
        }
        try:
            async with session.get(ITEM_SRCH_URL, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    docs = data.get("response", {}).get("docs", [])
                    for d in docs:
                        doc = d.get("doc", {})
                        api_isbn = normalize_isbn(doc.get("isbn13", ""))
                        if api_isbn == isbn: # 엄격한 대조
                            results.append({
                                "isbn13": api_isbn,
                                "title": doc.get("bookname", ""),
                                "vol": doc.get("vol", "").strip(),
                                "normalized_title": normalize_title(doc.get("bookname", ""))
                            })
        except Exception as e:
            pass

    # 2. 제목 검색 시도 (결과가 없거나 ISBN이 없는 경우)
    if not results and title:
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": PANGYO_LIB_CODE,
            "type": "TITLE",
            "keyword": title,
            "startDt": "2000-01-01",
            "endDt": "2025-12-31",
            "pageNo": 1,
            "pageSize": 100,
            "format": "json"
        }
        try:
            async with session.get(ITEM_SRCH_URL, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    docs = data.get("response", {}).get("docs", [])
                    norm_target_title = normalize_title(title)
                    for d in docs:
                        doc = d.get("doc", {})
                        api_title = doc.get("bookname", "")
                        api_norm_title = normalize_title(api_title)
                        # 제목이 포함되거나 포함하는 경우 매칭
                        if norm_target_title in api_norm_title or api_norm_title in norm_target_title:
                            results.append({
                                "isbn13": normalize_isbn(doc.get("isbn13", "")),
                                "title": api_title,
                                "vol": doc.get("vol", "").strip(),
                                "normalized_title": api_norm_title
                            })
        except Exception as e:
            pass
            
    return results

def find_duplicate_callnos():
    """중복된 청구기호를 가진 책들 찾기"""
    print("🔍 중복된 청구기호 검색 중...")
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

async def add_volume_info_refined():
    log_file = open("volume_update_log_v3.txt", "w", encoding="utf-8")
    def log(msg):
        print(msg, flush=True)
        log_file.write(msg + "\n")
        log_file.flush()
        
    log("\n" + "="*60)
    log("📚 중복 청구기호 책들에 권차정보 추가 (ISBN/Title Refined V3)")
    log("="*60 + "\n")
    
    duplicates = find_duplicate_callnos()
    if not duplicates:
        log("✅ 중복된 청구기호가 없습니다.")
        log_file.close()
        return
    
    total_books_sum = sum(len(v) for v in duplicates.values())
    log(f"\n📊 총 {len(duplicates)}개 그룹, {total_books_sum}권의 도서 처리 예정\n")
    
    updated_count = 0
    matched_by_isbn = 0
    matched_by_title_exact = 0
    matched_by_title_partial = 0
    failed_count = 0
    
    # 캐시 (ISBN -> API 결과)
    isbn_cache = {}
    # 캐시 (정규화된 제목 -> API 결과)
    title_cache = {}
    
    async with aiohttp.ClientSession() as session:
        for idx, (callno, books_list) in enumerate(duplicates.items(), 1):
            log(f"\n[{idx}/{len(duplicates)}] 📂 청구기호: {callno} ({len(books_list)}권)")
            
            for book in books_list:
                db_id = book["id"]
                db_isbn = normalize_isbn(book.get("isbn") or "")
                db_title = book.get("title") or ""
                db_norm_title = normalize_title(db_title)
                
                log(f"  📖 처리 중: {db_title[:20]}... (ISBN: {db_isbn})")
                
                api_results = []
                # 1. ISBN으로 캐시 확인 또는 API 호출
                if db_isbn:
                    if db_isbn in isbn_cache:
                        api_results = isbn_cache[db_isbn]
                    else:
                        api_results = await fetch_book_info_from_api(session, isbn=db_isbn)
                        isbn_cache[db_isbn] = api_results
                        await asyncio.sleep(0.3)
                
                # 2. ISBN 결과가 없고 제목이 있으면 제목으로 캐시 확인 또는 API 호출
                if not api_results and db_norm_title:
                    if db_norm_title in title_cache:
                        api_results = title_cache[db_norm_title]
                    else:
                        api_results = await fetch_book_info_from_api(session, title=db_title)
                        title_cache[db_norm_title] = api_results
                        await asyncio.sleep(0.3)
                
                matched_vol = None
                match_method = ""
                
                if api_results:
                    # 1. ISBN 매칭 시도
                    if db_isbn:
                        for res in api_results:
                            if res["isbn13"] == db_isbn and res["vol"]:
                                matched_vol = res["vol"]
                                match_method = "ISBN"
                                break
                    
                    # 2. 제목 정확 매칭 시도
                    if not matched_vol:
                        for res in api_results:
                            if res["normalized_title"] == db_norm_title and res["vol"]:
                                matched_vol = res["vol"]
                                match_method = "Title_Exact"
                                break
                    
                    # 3. 제목 부분 매칭 시도
                    if not matched_vol and len(db_norm_title) >= 3:
                        for res in api_results:
                            api_norm_title = res["normalized_title"]
                            if api_norm_title and (db_norm_title in api_norm_title or api_norm_title in db_norm_title):
                                if res["vol"]:
                                    matched_vol = res["vol"]
                                    match_method = "Title_Partial"
                                    break
                
                if matched_vol:
                    try:
                        supabase.table("childbook_items").update({"vol": matched_vol}).eq("id", db_id).execute()
                        log(f"    ✅ [{match_method}] 매칭 성공! vol: '{matched_vol}'")
                        updated_count += 1
                        if match_method == "ISBN": matched_by_isbn += 1
                        elif match_method == "Title_Exact": matched_by_title_exact += 1
                        else: matched_by_title_partial += 1
                    except Exception as e:
                        log(f"    ❌ 업데이트 실패: {e}")
                        failed_count += 1
                else:
                    log(f"    ⚠️ 매칭 실패")
                    failed_count += 1

    log(f"\n" + "="*60)
    log(f"✅ 총 {updated_count}권 업데이트 완료")
    log(f"   - ISBN 매칭: {matched_by_isbn}")
    log(f"   - 제목 정확 매칭: {matched_by_title_exact}")
    log(f"   - 제목 부분 매칭: {matched_by_title_partial}")
    log(f"❌ 매칭 실패: {failed_count}권")
    log("="*60)
    log_file.close()

if __name__ == "__main__":
    asyncio.run(add_volume_info_refined())
