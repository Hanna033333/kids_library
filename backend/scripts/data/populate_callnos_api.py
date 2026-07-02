#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
도서관 정보나루 API를 사용하여 전국 7대 도서관의 청구기호를 일괄 수집하여 DB에 적재하는 파이프라인.

수정 이력:
- 제목 유사도 검증 제거 → ISBN 매칭만 신뢰 (오매칭 방지 목적이었으나 오히려 아동 단어 포함 시 과다 통과)
- DB UNIQUE 제약 사전 검증 로직 추가
- Checkpoint 파일 기반 중단 재시작 지원 추가
"""

import sys
import os
import asyncio
import aiohttp
import argparse
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

sys.path.append("/Users/1004823/Desktop/kids_library/backend")
os.chdir("/Users/1004823/Desktop/kids_library/backend")

from core.database import supabase
from core.config import DATA4LIBRARY_KEY
from services.loan_status import LIBRARY_CODE_MAP

# 전역 동시성 세마포어 (지연 로딩으로 asyncio Event Loop 바인딩 에러 방지)
GLOBAL_SEMAPHORE = None

def get_semaphore() -> asyncio.Semaphore:
    global GLOBAL_SEMAPHORE
    if GLOBAL_SEMAPHORE is None:
        GLOBAL_SEMAPHORE = asyncio.Semaphore(5)
    return GLOBAL_SEMAPHORE

# 체크포인트 파일 경로 (중단 시 재시작 지원)
CHECKPOINT_PATH = Path("/Users/1004823/Desktop/kids_library/backend/scripts/data/.populate_checkpoint.json")


# ─────────────────────────────────────────────
# 4. UNIQUE 제약 사전 확인 (on_conflict 안전성 확보)
# ─────────────────────────────────────────────
def verify_unique_constraint() -> bool:
    """
    book_library_info 테이블에 (book_id, library_name) 복합 UNIQUE 제약이 존재하는지 확인합니다.
    존재하지 않으면 UPSERT 대신 INSERT로 동작해 중복 행이 쌓이므로, 반드시 사전 확인이 필요합니다.
    """
    try:
        # 실제 존재하는 book_id 1개 조회 (외래키 제약조건 위반 방지)
        res_book = supabase.table("childbook_items").select("id").limit(1).execute()
        if not res_book.data:
            print("⚠️ DB에 책 데이터가 존재하지 않아 제약 조건 검증을 건너뜁니다.")
            return False
            
        real_book_id = res_book.data[0]["id"]
        
        # 같은 book_id + library_name 조합으로 UPSERT 테스트 수행
        test_data = {
            "book_id": real_book_id,
            "library_name": "__constraint_check__",
            "callno": "TEST"
        }
        supabase.table("book_library_info").upsert(test_data, on_conflict="book_id, library_name").execute()
        supabase.table("book_library_info").upsert(test_data, on_conflict="book_id, library_name").execute()
        # 중복 삽입 후 행 수 확인
        res = supabase.table("book_library_info")\
            .select("id")\
            .eq("book_id", real_book_id)\
            .eq("library_name", "__constraint_check__")\
            .execute()
        count = len(res.data)
        # 정리 (흔적 지우기)
        supabase.table("book_library_info").delete().eq("book_id", real_book_id).eq("library_name", "__constraint_check__").execute()
        if count == 1:
            print("✅ DB UNIQUE 제약 확인: 정상 (on_conflict upsert 작동)")
            return True
        else:
            print(f"❌ DB UNIQUE 제약 미설정: 동일 row가 {count}개 생성됨. Supabase SQL Editor에서 아래 쿼리 실행 필요:")
            print("   ALTER TABLE book_library_info ADD CONSTRAINT book_library_info_book_id_library_name_key UNIQUE (book_id, library_name);")
            return False
    except Exception as e:
        print(f"⚠️ UNIQUE 제약 확인 중 오류 발생: {e}")
        print("   Supabase SQL Editor에서 수동으로 UNIQUE (book_id, library_name) 인덱스를 확인하세요.")
        return False


# ─────────────────────────────────────────────
# 5. 체크포인트 저장/로드 (중단 재시작 지원)
# ─────────────────────────────────────────────
def load_checkpoint() -> Dict:
    """마지막으로 처리된 book_id와 도서관명을 불러옵니다."""
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, "r") as f:
            data = json.load(f)
            print(f"📌 체크포인트 로드: 마지막 처리 book_id={data.get('last_book_id')}, 도서관={data.get('last_library')}")
            return data
    return {}


def save_checkpoint(lib_name: str, book_id: int):
    """현재 처리 위치를 체크포인트 파일에 저장합니다."""
    data = {
        "last_library": lib_name,
        "last_book_id": book_id,
        "saved_at": datetime.now().isoformat()
    }
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(data, f, ensure_ascii=False)


def clear_checkpoint():
    """파이프라인 성공적 완료 후 체크포인트 파일을 삭제합니다."""
    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()
        print("🗑️ 체크포인트 파일 삭제 (성공적 완료)")


# ─────────────────────────────────────────────
# API 호출 (2. ISBN만 신뢰 - 제목 유사도 제거)
# ─────────────────────────────────────────────
class APIQuotaExceededError(Exception):
    """정보나루 API가 errCode(예: outOflimit)를 HTTP 200으로 반환할 때 발생.
    이 에러를 조용히 삼키면 '미소장'으로 오판되어 데이터가 거짓으로 비게 되므로 반드시 상위로 전파해야 함."""
    pass


async def fetch_and_parse_callno(session: aiohttp.ClientSession, isbn: str, lib_code: str) -> Optional[str]:
    """
    정보나루 itemSrch API를 이용해 ISBN 기반으로 특정 도서관의 청구기호를 조회하고 조합합니다.
    ISBN이 고유 식별자이므로 제목 유사도 검증 없이 ISBN 매칭만으로 신뢰합니다.
    """
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

                # 정보나루는 한도초과 등 에러도 HTTP 200으로 응답하므로 errCode를 명시적으로 검사해야 함
                err_code = data.get("response", {}).get("errCode")
                if err_code:
                    err_msg = data.get("response", {}).get("error", err_code)
                    raise APIQuotaExceededError(f"[{err_code}] {err_msg}")

                docs = data.get("response", {}).get("docs", [])
                if not docs:
                    return None  # 해당 도서관 미소장
                
                doc = docs[0].get("doc", {})
                class_no = doc.get("class_no", "")
                call_numbers = doc.get("callNumbers", [])
                
                sep_code = ""
                book_code = ""
                
                if call_numbers:
                    cn = call_numbers[0].get("callNumber", {})
                    sep_code = cn.get("separate_shelf_code", "")
                    book_code = cn.get("book_code", "")
                
                # 청구기호 성립 최소 요건: 분류기호 + 도서기호 필수
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


# ─────────────────────────────────────────────
# 도서관별 수집 (직렬 도서관, 병렬 책 처리)
# ─────────────────────────────────────────────
async def populate_library(
    session: aiohttp.ClientSession,
    lib_name: str,
    lib_code: str,
    books: List[Dict],
    start_book_id: int = 0
) -> Dict:
    """한 도서관에 대해 청구기호가 없는 도서들을 채웁니다."""
    print(f"\n📚 [{lib_name}] 수집 시작 (대상: {len(books)}권)")
    
    # 1. 이미 존재하는 청구기호 book_id 조회 (중복 API 호출 방지)
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
        print(f"  ⚠️ 기존 데이터 확인 중 오류 (계속 진행): {e}")
    
    # 2. 체크포인트 기준 이후의 책 + 기존 미수집 책만 필터링
    target_books = [b for b in books if b["id"] not in existing_ids and b["id"] >= start_book_id]
    print(f"  ⏭️ 기수집 스킵: {len(existing_ids)}권 / 체크포인트 이후 신규 대상: {len(target_books)}권")
    
    if not target_books:
        return {"total": 0, "success": 0, "skipped": len(existing_ids)}
    
    success_count = 0
    fail_count = 0
    last_processed_id = start_book_id

    async def process_book(book):
        nonlocal success_count, fail_count, last_processed_id
        callno = await fetch_and_parse_callno(session, book["isbn"], lib_code)
        if callno:
            try:
                data = {
                    "book_id": book["id"],
                    "library_name": lib_name,
                    "callno": callno,
                    "updated_at": "now()"
                }
                supabase.table("book_library_info").upsert(data, on_conflict="book_id, library_name").execute()
                success_count += 1
            except Exception:
                fail_count += 1
        last_processed_id = book["id"]
        # 체크포인트 주기적 저장 (매 50권마다)
        if (success_count + fail_count) % 50 == 0:
            save_checkpoint(lib_name, last_processed_id)
        await asyncio.sleep(0.3)  # API 쿨다운

    # 3. 책 단위 병렬 처리 (세마포어로 최대 5개 동시)
    tasks = [process_book(book) for book in target_books]
    try:
        await asyncio.gather(*tasks)
    except APIQuotaExceededError:
        # API 한도 초과는 이 도서관만의 문제가 아니라 전역 문제이므로,
        # 지금까지 처리한 지점을 체크포인트로 남기고 파이프라인 전체를 중단시킨다.
        save_checkpoint(lib_name, last_processed_id)
        raise

    # 도서관 수집 완료 시 체크포인트 갱신
    save_checkpoint(lib_name, last_processed_id)
    print(f"  ✅ [{lib_name}] 완료: 적재 {success_count}권 / 실패 {fail_count}권 / 미소장(스킵) {len(target_books) - success_count - fail_count}권")
    
    return {"total": len(target_books), "success": success_count, "fail": fail_count, "skipped": len(existing_ids)}


# ─────────────────────────────────────────────
# 메인 파이프라인
# ─────────────────────────────────────────────
async def main_pipeline():
    parser = argparse.ArgumentParser(description="도서관 정보나루 청구기호 일괄 적재기")
    parser.add_argument("--limit", type=int, default=100, help="한 번에 로드해서 처리할 책 권수 (기본: 100)")
    parser.add_argument("--offset", type=int, default=0, help="도서 로드 시작점 (Offset, 기본: 0)")
    parser.add_argument("--resume", action="store_true", help="체크포인트부터 재개 (중단된 작업 이어받기)")
    args = parser.parse_args()
    
    if not DATA4LIBRARY_KEY:
        print("❌ DATA4LIBRARY_KEY 환경 변수가 설정되어 있지 않습니다.")
        return
    
    print("=" * 80)
    print(f"🚀 전국 7대 도서관 청구기호 수집 파이프라인 시작")
    print(f"   LIMIT: {args.limit} | OFFSET: {args.offset} | RESUME: {args.resume}")
    print("=" * 80)
    
    # 4. UNIQUE 제약 사전 검증
    if not verify_unique_constraint():
        print("\n❌ UNIQUE 제약이 확인되지 않아 파이프라인을 중단합니다.")
        print("   Supabase SQL Editor에서 아래 SQL을 실행한 후 재시도하세요:")
        print("   ALTER TABLE book_library_info ADD CONSTRAINT book_library_info_unique_book_lib UNIQUE (book_id, library_name);")
        return
    
    # 5. 체크포인트 로드
    checkpoint = {}
    start_book_id = 0
    resume_library = None
    if args.resume:
        checkpoint = load_checkpoint()
        start_book_id = checkpoint.get("last_book_id", 0)
        resume_library = checkpoint.get("last_library")
        if resume_library:
            print(f"🔄 '{resume_library}' 도서관부터, book_id>={start_book_id} 기준으로 재개합니다.")
    
    # 도서 목록 조회
    try:
        res = supabase.table("childbook_items")\
            .select("id, isbn, title")\
            .not_.is_("isbn", "null")\
            .order("id")\
            .range(args.offset, args.offset + args.limit - 1)\
            .execute()
        raw_books = res.data
        
        books = []
        for b in raw_books:
            isbn = str(b.get("isbn", "")).strip()
            if len(isbn) == 13 and not isbn.endswith("000000"):
                books.append({"id": b["id"], "isbn": isbn, "title": b["title"]})
        
        print(f"✅ 유효 ISBN 도서 {len(books)}권 로드 완료 (전체 로드: {len(raw_books)}권)")
    except Exception as e:
        print(f"❌ DB 도서 조회 실패: {e}")
        return
    
    if not books:
        print("수집 대상 유효 도서가 없습니다.")
        return
    
    # 도서관 직렬 처리 (3. 병렬 전환 대신 안정성 우선 직렬 유지)
    total_stats = {}
    lib_list = [
        (lib_name, lib_code)
        for lib_name, lib_code in LIBRARY_CODE_MAP.items()
        if lib_name not in ["판교도서관", "송파어린이도서관"]
    ]
    
    # resume 시 해당 도서관부터 시작
    if resume_library and resume_library in LIBRARY_CODE_MAP:
        lib_names = [k for k in LIBRARY_CODE_MAP]
        start_idx = lib_names.index(resume_library)
        lib_list = lib_list[start_idx:]
    
    timeout = aiohttp.ClientTimeout(total=600)
    quota_exceeded = False
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for i, (lib_name, lib_code) in enumerate(lib_list):
            # resume 시 첫 번째 도서관만 checkpoint book_id 적용, 이후는 0부터
            effective_start = start_book_id if (args.resume and i == 0) else 0
            try:
                stats = await populate_library(session, lib_name, lib_code, books, start_book_id=effective_start)
                total_stats[lib_name] = stats
            except APIQuotaExceededError as e:
                print(f"\n🛑 [{lib_name}] 처리 중 정보나루 API 한도 초과 감지: {e}")
                print("   지금까지의 결과는 '미소장'이 아니라 API 실패이므로 신뢰할 수 없습니다.")
                print("   체크포인트가 저장되었으니, 한도가 초기화된 뒤 --resume 옵션으로 이어서 실행하세요.")
                quota_exceeded = True
                break

    if not quota_exceeded:
        clear_checkpoint()

    print("\n" + "=" * 80)
    print("📊 최종 수집 결과 요약")
    print("=" * 80)
    for lib_name, stats in total_stats.items():
        success = stats.get("success", 0)
        total = stats.get("total", 0)
        skipped = stats.get("skipped", 0)
        rate = f"{success / total * 100:.1f}%" if total > 0 else "N/A"
        print(f"  {lib_name}: 신규 {success}/{total}권 적재 ({rate}) | 기수집 스킵 {skipped}권")
    print("=" * 80)
    if quota_exceeded:
        print("⚠️ API 한도 초과로 파이프라인이 중단되었습니다. 위 요약에 없는 도서관은 미실행 상태입니다.")
    else:
        print("🎉 파이프라인 정상 완료.")


if __name__ == "__main__":
    asyncio.run(main_pipeline())
