#!/usr/bin/env python3
"""추석 도서 7권의 청구기호를 Data4Library API로 수집하여 DB에 적재."""

import sys, os, asyncio, aiohttp

sys.path.insert(0, "/Users/1004823/Desktop/kids_library/backend")
os.chdir("/Users/1004823/Desktop/kids_library/backend")

from dotenv import load_dotenv
load_dotenv(".env")

from core.database import supabase
from core.config import DATA4LIBRARY_KEY
from services.loan_status import LIBRARY_CODE_MAP

TARGET_IDS = [11519, 11522, 11523, 11524, 11525, 11526, 11527]

SEMAPHORE = asyncio.Semaphore(5)


async def fetch_callno(session: aiohttp.ClientSession, isbn: str, lib_code: str):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": lib_code,
        "isbn13": isbn,
        "type": "ALL",
        "format": "json",
    }
    async with SEMAPHORE:
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("response", {}).get("errCode"):
                    raise Exception(f"API 에러: {data['response']}")
                docs = data.get("response", {}).get("docs", [])
                if not docs:
                    return None
                doc = docs[0].get("doc", {})
                class_no = doc.get("class_no", "")
                call_numbers = doc.get("callNumbers", [])
                sep_code = book_code = ""
                if call_numbers:
                    cn = call_numbers[0].get("callNumber", {})
                    sep_code = cn.get("separate_shelf_code", "")
                    book_code = cn.get("book_code", "")
                if not class_no or not book_code:
                    return None
                full = (f"{sep_code.strip()} " if sep_code else "") + f"{class_no.strip()}-{book_code.strip()}"
                return full.strip()
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            print(f"    ⚠️ fetch 오류: {e}")
            return None


async def main():
    if not DATA4LIBRARY_KEY:
        print("❌ DATA4LIBRARY_KEY 없음")
        return

    # 대상 도서 ISBN 조회
    res = supabase.table("childbook_items").select("id, isbn, title").in_("id", TARGET_IDS).execute()
    books = [b for b in res.data if b.get("isbn") and len(str(b["isbn"])) == 13]
    print(f"✅ 대상 도서 {len(books)}권 로드 (ISBN 유효)")
    for b in books:
        print(f"   [{b['id']}] {b['title'][:30]} / ISBN: {b['isbn']}")

    # 판교·송파 포함 전체 도서관 API 조회
    api_libs = LIBRARY_CODE_MAP
    print(f"\n📚 조회 도서관: {list(api_libs.keys())}\n")

    inserted = 0
    not_found = []

    async with aiohttp.ClientSession() as session:
        for book in books:
            isbn = str(book["isbn"])
            book_found_any = False
            for lib_name, lib_code in api_libs.items():
                callno = await fetch_callno(session, isbn, lib_code)
                if callno:
                    supabase.table("book_library_info").upsert(
                        {"book_id": book["id"], "library_name": lib_name, "callno": callno},
                        on_conflict="book_id, library_name",
                    ).execute()
                    print(f"  ✅ [{book['id']}] {book['title'][:22]} | {lib_name}: {callno}")
                    inserted += 1
                    book_found_any = True
                else:
                    print(f"  ─  [{book['id']}] {book['title'][:22]} | {lib_name}: 미소장")
                await asyncio.sleep(0.3)

            if not book_found_any:
                not_found.append(book["title"])

    print(f"\n{'='*60}")
    print(f"🎉 완료: {inserted}건 적재")
    if not_found:
        print(f"⚠️ 전 도서관 미소장: {not_found}")


if __name__ == "__main__":
    asyncio.run(main())
