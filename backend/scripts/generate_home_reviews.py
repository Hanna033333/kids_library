"""
홈 화면 노출 도서 시드 리뷰 생성 스크립트
- 칼데콧, 어린이도서연구회, 연령별(4-7세), 이번 주 큐레이션(명절/우리문화/장애)
- 리뷰 없는 도서만 처리 (--skip-existing 기본)
"""
import os
import sys
import json
import time
import random
import logging
from typing import Optional, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

# generate_seed_reviews에서 핵심 함수 재사용
from scripts.generate_seed_reviews import generate_reviews_for_book, insert_reviews

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 오늘 홈에 노출되는 섹션 정의 (2026-09-01 기준)
HOME_SECTIONS = [
    {"name": "칼데콧",         "filter": "caldecott",     "type": "ilike"},
    {"name": "어린이도서연구회", "filter": "어린이도서연구회", "type": "ilike"},
    {"name": "4-7세 연령별",   "filter": "4-7",            "type": "age"},
    {"name": "명절 큐레이션",   "filter": "명절",            "type": "tag"},
    {"name": "우리문화 큐레이션","filter": "우리문화",         "type": "tag"},
    {"name": "장애 큐레이션",   "filter": "장애",            "type": "tag"},
]


def fetch_section_books(section: dict, limit: int = 14) -> List[dict]:
    """섹션별 도서 조회 (넉넉히 14권 — 로테이션 대비)"""
    fields = "id, title, author, age, category, curation_tag, national_loan_count, description"
    q = supabase.table("childbook_items").select(fields)

    t = section["type"]
    f = section["filter"]

    if t == "ilike":
        q = q.ilike("curation_tag", f"%{f}%")
    elif t == "age":
        q = q.eq("age", f)
    elif t == "tag":
        # 첫 번째 태그 정밀 매칭 (exact or leading)
        q = q.or_(f'curation_tag.eq."{f}",curation_tag.like."{f},%"')

    result = q.order("national_loan_count", desc=True).limit(limit).execute()
    return result.data or []


def get_reviewed_ids() -> set:
    """이미 리뷰가 있는 book_id 집합 반환"""
    all_ids = set()
    offset = 0
    while True:
        batch = supabase.table("book_reviews").select("book_id").range(offset, offset + 999).execute()
        for r in batch.data:
            all_ids.add(r["book_id"])
        if len(batch.data) < 1000:
            break
        offset += 1000
    return all_ids


def main():
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    logger.info("=== 홈 화면 노출 도서 리뷰 생성 시작 ===")

    # 1. 이미 리뷰 있는 ID 수집
    logger.info("기존 리뷰 현황 조회 중...")
    reviewed_ids = get_reviewed_ids()
    logger.info(f"현재 리뷰 있는 도서: {len(reviewed_ids)}권")

    # 2. 섹션별 도서 수집 & 중복 제거
    books_map: dict[int, dict] = {}
    for section in HOME_SECTIONS:
        books = fetch_section_books(section)
        logger.info(f"  [{section['name']}] {len(books)}권 조회")
        for b in books:
            books_map[b["id"]] = b

    all_home_books = list(books_map.values())
    logger.info(f"\n홈 전체 노출 도서 (중복 제거): {len(all_home_books)}권")

    # 3. 리뷰 없는 도서만 필터
    target_books = [b for b in all_home_books if b["id"] not in reviewed_ids]
    already_have = len(all_home_books) - len(target_books)
    logger.info(f"이미 리뷰 있음: {already_have}권  |  생성 필요: {len(target_books)}권")

    if not target_books:
        logger.info("✅ 모든 홈 노출 도서에 리뷰가 이미 있습니다!")
        return

    # 4. 리뷰 생성 & 삽입
    success = 0
    fail = 0
    total_inserted = 0

    for i, book in enumerate(target_books, 1):
        book_id = book["id"]
        title = book.get("title", f"ID:{book_id}")
        count = random.randint(3, 4)  # 도서당 3~4개

        logger.info(f"[{i}/{len(target_books)}] '{title}' (연령: {book.get('age')}) — {count}개 생성 중...")

        reviews = generate_reviews_for_book(book, count=count)
        if not reviews:
            logger.error(f"  ❌ Gemini 생성 실패")
            fail += 1
            time.sleep(1)
            continue

        inserted = insert_reviews(book_id, title, reviews)
        if inserted > 0:
            logger.info(f"  ✅ {inserted}개 적재 완료")
            total_inserted += inserted
            success += 1
        else:
            logger.error(f"  ❌ DB 삽입 실패")
            fail += 1

        time.sleep(1.2)  # API Rate Limit 방지

    logger.info(f"\n=== 완료 ===")
    logger.info(f"성공: {success}권 | 실패: {fail}권 | 총 리뷰 적재: {total_inserted}개")

    # 5. 최종 커버리지 출력
    reviewed_ids_after = get_reviewed_ids()
    home_ids = set(books_map.keys())
    covered = home_ids & reviewed_ids_after
    logger.info(f"\n홈 노출 도서 리뷰 커버리지: {len(covered)}/{len(home_ids)}권 ({len(covered)/len(home_ids)*100:.1f}%)")


if __name__ == "__main__":
    main()
