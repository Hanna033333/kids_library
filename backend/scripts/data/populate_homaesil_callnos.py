#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
수원시립호매실도서관 (141552) 청구기호 수집 스크립트
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

LIB_NAME = "수원시립호매실도서관"
LIB_CODE = "141552"

SEMAPHORE = None

def get_semaphore():
    global SEMAPHORE
    if SEMAPHORE is None:
        SEMAPHORE = asyncio.Semaphore(6)
    return SEMAPHORE


class APIQuotaExceededError(Exception):
    pass


async def fetch_and_parse_callno(session: aiohttp.ClientSession, isbn: str, lib_code: str) -> Optional[str]:
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


async def main():
    if not DATA4LIBRARY_KEY:
        print("❌ DATA4LIBRARY_KEY 가 없습니다.")
        return

    print(f"🚀 [{LIB_NAME}] 청구기호 수집 시작...")
    
    # 1. 도서 로드
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

    # 기수집 확인
    existing_ids = set()
    book_ids = [b["id"] for b in all_books]
    for i in range(0, len(book_ids), 500):
        chunk = book_ids[i:i + 500]
        res = supabase.table("book_library_info")\
            .select("book_id")\
            .eq("library_name", LIB_NAME)\
            .in_("book_id", chunk)\
            .not_.is_("callno", "null")\
            .execute()
        for rec in res.data:
            existing_ids.add(rec["book_id"])

    target_books = [b for b in all_books if b["id"] not in existing_ids]
    print(f"  ⏭️ 기수집 스킵: {len(existing_ids)}권 / 신규 조회 대상: {len(target_books)}권")

    if not target_books:
        print(f"✅ 이미 모든 도서 수집이 완료되었습니다.")
        return

    success_count = 0
    fail_count = 0
    not_found_count = 0
    processed_count = 0

    timeout = aiohttp.ClientTimeout(total=1800)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async def process_book(book):
            nonlocal success_count, fail_count, not_found_count, processed_count
            try:
                callno = await fetch_and_parse_callno(session, book["isbn"], LIB_CODE)
                if callno:
                    data = {
                        "book_id": book["id"],
                        "library_name": LIB_NAME,
                        "callno": callno,
                        "updated_at": datetime.now().isoformat()
                    }
                    supabase.table("book_library_info").upsert(data, on_conflict="book_id, library_name").execute()
                    success_count += 1

                    if not book.get("pangyo_callno") or book.get("pangyo_callno") == "없음":
                        supabase.table("childbook_items").update({"pangyo_callno": callno}).eq("id", book["id"]).execute()
                else:
                    not_found_count += 1
            except APIQuotaExceededError:
                raise
            except Exception:
                fail_count += 1

            processed_count += 1
            if processed_count % 100 == 0 or processed_count == len(target_books):
                print(f"  진행률: [{processed_count}/{len(target_books)}] (성공: {success_count}권, 미소장: {not_found_count}권, 실패: {fail_count}권)")

            await asyncio.sleep(0.05)

        batch_size = 20
        for i in range(0, len(target_books), batch_size):
            batch = target_books[i:i + batch_size]
            await asyncio.gather(*[process_book(b) for b in batch])

    print("\n" + "=" * 70)
    print(f"✅ [{LIB_NAME}] 수집 완료: 총 소장 청구기호 {success_count + len(existing_ids)}권 (신규 적재: {success_count}권, 미소장: {not_found_count}권, 오류: {fail_count}권)")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
