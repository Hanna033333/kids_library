#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
신규 4개 도서관(아이꿈 작은도서관, 부산광역시 강서기적의도서관, 하남시 위례도서관, 손기정 어린이도서관) 청구기호 수집 스크립트
"""

import sys
import os
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

BACKEND_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BACKEND_DIR))
os.chdir(str(BACKEND_DIR))

from core.database import supabase
from core.config import DATA4LIBRARY_KEY

TARGET_LIBRARIES = {
    "아이꿈 작은도서관": "726304",
    "부산광역시 강서기적의도서관": "126156",
    "하남시 위례도서관": "141636",
    "손기정 어린이도서관": "111498",
}

SEMAPHORE = None

def get_semaphore():
    global SEMAPHORE
    if SEMAPHORE is None:
        SEMAPHORE = asyncio.Semaphore(6)
    return SEMAPHORE


class APIQuotaExceededError(Exception):
    pass


async def fetch_and_parse_callno(session: aiohttp.ClientSession, isbn: str, lib_code: str) -> Optional[str]:
    """정보나루 itemSrch API를 이용해 청구기호를 추출 및 조합합니다."""
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": lib_code,
        "isbn13": isbn,
        "type": "ALL",
        "format": "json"
    }

    async with get_semaphore():
        try:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                err_code = data.get("response", {}).get("errCode")
                if err_code:
                    err_msg = data.get("response", {}).get("error", err_code)
                    raise APIQuotaExceededError(f"[{err_code}] {err_msg}")

                docs = data.get("response", {}).get("docs", [])
                if not docs:
                    return None

                doc = docs[0].get("doc", {})
                class_no = doc.get("class_no", "")
                call_numbers = doc.get("callNumbers", [])

                sep_code = ""
                book_code = ""

                if call_numbers:
                    cn = call_numbers[0].get("callNumber", {})
                    sep_code = cn.get("separate_shelf_code", "")
                    book_code = cn.get("book_code", "")

                if not class_no or not book_code:
                    return None

                full_callno = ""
                if sep_code:
                    full_callno += f"{sep_code.strip()} "
                full_callno += f"{class_no.strip()}-{book_code.strip()}"

                return full_callno.strip()

        except asyncio.TimeoutError:
            return None
        except APIQuotaExceededError:
            raise
        except Exception:
            return None


async def collect_for_library(session: aiohttp.ClientSession, lib_name: str, lib_code: str, books: List[Dict]) -> Dict:
    print(f"\n========================================================")
    print(f"📚 [{lib_name}] 청구기호 수집 시작 (전체 도서: {len(books)}권)")
    print(f"========================================================")

    # 1. 이미 존재하는 청구기호 book_id 조회
    existing_ids = set()
    try:
        book_ids = [b["id"] for b in books]
        chunk_size = 500
        for i in range(0, len(book_ids), chunk_size):
            chunk = book_ids[i:i + chunk_size]
            res = supabase.table("book_library_info")\
                .select("book_id")\
                .eq("library_name", lib_name)\
                .in_("book_id", chunk)\
                .not_.is_("callno", "null")\
                .execute()
            for rec in res.data:
                existing_ids.add(rec["book_id"])
    except Exception as e:
        print(f"  ⚠️ 기존 데이터 확인 오류: {e}")

    target_books = [b for b in books if b["id"] not in existing_ids]
    print(f"  ⏭️ 기수집 스킵: {len(existing_ids)}권 / 신규 조회 대상: {len(target_books)}권")

    if not target_books:
        return {"total": len(books), "success": 0, "skipped": len(existing_ids), "not_found": 0}

    success_count = 0
    fail_count = 0
    not_found_count = 0
    processed_count = 0

    async def process_book(book):
        nonlocal success_count, fail_count, not_found_count, processed_count
        try:
            callno = await fetch_and_parse_callno(session, book["isbn"], lib_code)
            if callno:
                data = {
                    "book_id": book["id"],
                    "library_name": lib_name,
                    "callno": callno,
                    "updated_at": datetime.now().isoformat()
                }
                supabase.table("book_library_info").upsert(data, on_conflict="book_id, library_name").execute()
                success_count += 1

                # 메인 테이블 pangyo_callno가 비어있는 경우 동기화
                if not book.get("pangyo_callno") or book.get("pangyo_callno") == "없음":
                    supabase.table("childbook_items").update({"pangyo_callno": callno}).eq("id", book["id"]).execute()
            else:
                not_found_count += 1
        except APIQuotaExceededError:
            raise
        except Exception as e:
            fail_count += 1

        processed_count += 1
        if processed_count % 100 == 0 or processed_count == len(target_books):
            print(f"  진행률: [{processed_count}/{len(target_books)}] (성공: {success_count}권, 미소장: {not_found_count}권, 실패: {fail_count}권)")

        await asyncio.sleep(0.05)

    # 청크 단위로 병렬 실행하여 안정성 확보
    batch_size = 20
    for i in range(0, len(target_books), batch_size):
        batch = target_books[i:i + batch_size]
        await asyncio.gather(*[process_book(b) for b in batch])

    print(f"  ✅ [{lib_name}] 완료: 수집 적재 {success_count}권 / 미소장 {not_found_count}권 / 오류 {fail_count}권")
    return {
        "total": len(target_books),
        "success": success_count,
        "not_found": not_found_count,
        "fail": fail_count,
        "skipped": len(existing_ids)
    }


async def main():
    if not DATA4LIBRARY_KEY:
        print("❌ DATA4LIBRARY_KEY 가 없습니다.")
        return

    print("🚀 신규 4개 도서관 청구기호 일괄 수집 시작...")
    
    # 1. 모든 유효 도서 로드
    all_books = []
    page_size = 1000
    offset = 0
    while True:
        res = supabase.table("childbook_items")\
            .select("id, title, isbn, pangyo_callno")\
            .not_.is_("isbn", "null")\
            .order("id")\
            .range(offset, offset + page_size - 1)\
            .execute()
        
        batch = res.data or []
        if not batch:
            break
        
        for b in batch:
            isbn = str(b.get("isbn", "")).strip()
            if len(isbn) == 13 and not isbn.endswith("000000"):
                all_books.append(b)
        
        offset += page_size
        if len(batch) < page_size:
            break

    print(f"📚 전체 수집 대상 유효 도서 수: {len(all_books)}권")

    timeout = aiohttp.ClientTimeout(total=1800)
    summary = {}
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for lib_name, lib_code in TARGET_LIBRARIES.items():
            try:
                stats = await collect_for_library(session, lib_name, lib_code, all_books)
                summary[lib_name] = stats
            except APIQuotaExceededError as e:
                print(f"🛑 API 한도 초과로 중단됨: {e}")
                break

    print("\n" + "=" * 70)
    print("📊 [신규 4개 도서관 청구기호 수집 최종 결과]")
    print("=" * 70)
    for lib_name, stats in summary.items():
        succ = stats.get("success", 0)
        skip = stats.get("skipped", 0)
        tot = succ + skip
        print(f"  🏛️ {lib_name}: 총 소장 청구기호 {tot}권 (신규 적재: {succ}권, 기존: {skip}권)")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
