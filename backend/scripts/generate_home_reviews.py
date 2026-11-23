"""
홈 화면 노출 도서 시드 리뷰 생성 스크립트
- 현재 날짜(KST) 기준 홈 화면에 노출되는 모든 섹션의 도서를 프론트엔드(page.tsx / home-api.ts)와 동일한 쿼리로 조회
  1. AI 주간 큐레이션 서가 (frontend/shared/weekly_schedule.json 기반 3개 태그, 각 14권)
  2. 50+ 전문 테마 큐레이션 쇼케이스 (기본 탭 '환경보호' + 인기 탭 6종, 각 14권)
  3. 2022 개정 교과서 수록도서 쇼케이스 ('전체' + 초등 1~6학년 탭, 각 6권)
  4. 칼데콧 수상작 (제목 오름차순 상위 14권)
  5. 어린이도서연구회 추천 (이번 주 주차 offset 기준 14권)
- 각 도서가 최소 2개~최대 4개의 리뷰(댓글)를 갖도록 부족분만 자동 생성 및 적재
"""
import argparse
import datetime
import json
import logging
import math
import os
import random
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Set, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import GEMINI_API_KEY, SUPABASE_KEY, SUPABASE_SERVICE_KEY, SUPABASE_URL
from supabase import create_client

from scripts.generate_seed_reviews import (
    BADGE_LIST,
    NICKNAME_POOL,
    generate_reviews_for_book,
)
import google.generativeai as genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)

FIELDS = "id, title, author, age, category, curation_tag, national_loan_count, description, image_url"

# ThemeCurationShowcase.tsx의 POPULAR_THEME_TABS와 동기화
POPULAR_THEME_TAGS = [
    ("테마: 초록 지구·환경", "환경보호"),
    ("테마: 잠자리·수면", "잠자리"),
    ("테마: 정겨운 명절", "명절"),
    ("테마: 상실과 위로", "상실"),
    ("테마: 상상·창의력", "상상력"),
    ("테마: 우리 문화 유산", "우리문화"),
    ("테마: 다름과 존중", "장애"),
]

# TextbookCurationShowcase.tsx의 TEXTBOOK_GRADE_TABS와 동기화
TEXTBOOK_GRADE_TAGS = [
    ("교과서: 전체", None),
    ("교과서: 초등 1학년", "초등1학년"),
    ("교과서: 초등 2학년", "초등2학년"),
    ("교과서: 초등 3학년", "초등3학년"),
    ("교과서: 초등 4학년", "초등4학년"),
    ("교과서: 초등 5학년", "초등5학년"),
    ("교과서: 초등 6학년", "초등6학년"),
]


def get_kst_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))


def get_week_number(now: datetime.datetime) -> int:
    start_of_year = datetime.datetime(now.year, 1, 1, tzinfo=now.tzinfo)
    return int((now - start_of_year).total_seconds() // (7 * 24 * 60 * 60))


def get_day_of_year(now: datetime.datetime) -> int:
    start_of_year = datetime.datetime(now.year, 1, 1, tzinfo=now.tzinfo)
    return int((now - start_of_year).total_seconds() // (24 * 60 * 60))


def seeded_shuffle(items: List[dict], seed: float) -> List[dict]:
    """frontend/lib/home-api.ts의 seededShuffle과 동일한 로직"""
    shuffled = list(items)
    for i in range(len(shuffled) - 1, 0, -1):
        x = math.sin(seed + i) * 10000
        r = x - math.floor(x)
        j = int(math.floor(r * (i + 1)))
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled


def visible_books_query():
    """frontend/lib/home-api.ts의 visibleBooks와 동일한 필터"""
    return (
        supabase.table("childbook_items")
        .select(FIELDS)
        .or_("is_hidden.is.null,is_hidden.eq.false")
        .not_.is_("image_url", "null")
        .neq("image_url", "")
        .not_.ilike("image_url", "%noimg%")
    )


def get_weekly_curation_tags(now_kst: datetime.datetime) -> List[tuple]:
    """frontend/shared/weekly_schedule.json에서 이번 주 주간 큐레이션 3개 로드"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    schedule_path = os.path.join(project_root, "frontend", "shared", "weekly_schedule.json")
    with open(schedule_path, "r", encoding="utf-8") as f:
        schedule = json.load(f)

    date_str = now_kst.strftime("%Y-%m-%d")
    matched = next((item for item in schedule if item["start"] <= date_str <= item["end"]), None)
    if matched:
        curations = matched["curations"]
    else:
        days_since_epoch = int(time.time() // (60 * 60 * 24))
        seed = days_since_epoch // 7
        lcg_state = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
        lcg_state = (lcg_state * 1664525 + 1013904223) & 0xFFFFFFFF
        target_idx = int((lcg_state / 0x100000000) * len(schedule))
        safe_idx = max(0, min(target_idx, len(schedule) - 1))
        curations = schedule[safe_idx]["curations"]

    return [(f"주간: {c['title']} ({c['tag']})", c["tag"]) for c in curations]


def fetch_books_by_tag(tag: str, limit: int = 14) -> List[dict]:
    """getBooksByTag 동일 쿼리 (첫 번째 태그 정밀 매칭 + confidence_score 내림차순)"""
    or_filter = f'curation_tag.eq."{tag}",curation_tag.like."{tag},%",curation_tag.eq."#{tag}",curation_tag.like."#{tag},%"'
    res = (
        visible_books_query()
        .or_(or_filter)
        .order("confidence_score", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


def fetch_textbook_books(grade_tag: str = None, limit: int = 6, now_kst: datetime.datetime = None) -> List[dict]:
    """getTextbookBooks 동일 쿼리"""
    q = visible_books_query().ilike("curation_tag", "%교과서수록%")
    if grade_tag:
        q = q.ilike("curation_tag", f"%{grade_tag}%")
    fetch_limit = max(limit * 3, 24)
    res = q.order("id", desc=False).limit(fetch_limit).execute()
    data = res.data or []
    if not data:
        return []
    seed = get_day_of_year(now_kst or get_kst_now()) * 0.001
    shuffled = seeded_shuffle(data, seed)
    return shuffled[: min(limit, len(shuffled))]


def fetch_caldecott_books(limit: int = 14) -> List[dict]:
    """getCaldecottBooks 동일 쿼리 (제목 오름차순)"""
    res = (
        visible_books_query()
        .ilike("curation_tag", "%caldecott%")
        .order("title", desc=False)
        .limit(limit)
        .execute()
    )
    return res.data or []


def fetch_research_council_books(limit: int = 14, now_kst: datetime.datetime = None) -> List[dict]:
    """getResearchCouncilBooks 동일 쿼리 (pool 100 중 주차 offset 슬라이싱)"""
    res = (
        visible_books_query()
        .ilike("curation_tag", "%어린이도서연구회%")
        .order("id", desc=False)
        .limit(100)
        .execute()
    )
    pool = res.data or []
    if not pool:
        return []
    max_offset = max(0, len(pool) - limit)
    offset = (get_week_number(now_kst or get_kst_now()) * limit) % (max_offset + 1) if max_offset > 0 else 0
    return pool[offset : offset + limit]


def get_existing_reviews_map() -> Dict[int, List[str]]:
    """book_id -> 기존 리뷰 닉네임 리스트 반환 (리뷰 개수 및 닉네임 중복 방지용)"""
    reviews_map: Dict[int, List[str]] = defaultdict(list)
    offset = 0
    while True:
        batch = (
            supabase.table("book_reviews")
            .select("book_id, nickname")
            .range(offset, offset + 999)
            .execute()
        )
        rows = batch.data or []
        for r in rows:
            reviews_map[r["book_id"]].append(r.get("nickname") or "")
        if len(rows) < 1000:
            break
        offset += 1000
    return reviews_map


def insert_reviews_safe(book_id: int, book_title: str, reviews: List[dict], existing_nicknames: Set[str]) -> int:
    """서비스 키 기반 안전 DB 삽입 (기존 닉네임 중복 방지)"""
    used_nicknames = set(existing_nicknames)
    inserted = 0

    for review in reviews:
        candidates = [n for n in NICKNAME_POOL if n not in used_nicknames] or NICKNAME_POOL
        nickname = random.choice(candidates)
        used_nicknames.add(nickname)

        selected_badges = [b for b in review.get("selected_badges", []) if b in BADGE_LIST]

        days_ago = random.randint(1, 60)
        hours_ago = random.randint(0, 23)
        created_at_time = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(time.time() - (days_ago * 86400 + hours_ago * 3600)),
        )

        content_text = (review.get("content") or "")[:500]
        if not content_text.strip():
            continue

        data_new = {
            "book_id": book_id,
            "nickname": nickname,
            "child_age": review.get("child_age"),
            "rating": int(round(min(5.0, max(1.0, float(review.get("rating", 4.5)))))),
            "selected_badges": selected_badges,
            "content": content_text,
            "comment": content_text,
            "created_at": created_at_time,
            "is_ai_generated": True,
        }

        try:
            result = supabase.table("book_reviews").insert(data_new).execute()
            if result.data:
                inserted += 1
            else:
                logger.error(f"[{book_title}] 빈 응답 반환")
        except Exception as e:
            logger.error(f"[{book_title}] DB 삽입 실패: {e}")

    return inserted


MODEL_FALLBACK_LIST = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
]


def _age_guide_short(age: str) -> str:
    if any(k in age for k in ["0-3", "0~3", "영아", "0세", "1세", "2세", "3세"]):
        return "0~3세 영아(child_age: 1세/2세/3세)"
    if any(k in age for k in ["8-12", "8~12", "초등", "8세", "9세", "10세", "11세", "12세"]):
        return "8~12세 초등(child_age: 8세~12세 또는 초등1~6, 영아 소재 절대 금지)"
    return "4~7세 유아(child_age: 4세/5세/6세/7세)"


def generate_reviews_batch(
    batch_items: List[Tuple[dict, int]],
    model_name: str,
) -> Dict[int, List[dict]]:
    """여러 도서(최대 10권)의 리뷰를 1회 Gemini API 호출로 일괄 생성"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name)

    books_spec = []
    for book, needed in batch_items:
        age = book.get("age") or ("8-12" if "초등" in (book.get("curation_tag") or "") else "4-7")
        books_spec.append(
            {
                "book_id": book["id"],
                "title": book.get("title", ""),
                "author": book.get("author", ""),
                "age_guide": _age_guide_short(age),
                "curation_tag": book.get("curation_tag", ""),
                "description": (book.get("description") or "")[:220],
                "count": needed,
            }
        )

    prompt = f"""당신은 3040 한국 부모님들이 도서 앱에 남기는 실제 도서 후기를 재현하는 전문가입니다.
아래 {len(books_spec)}권의 어린이 도서 각각에 대해 요청된 개수(`count`)만큼 자연스러운 부모 후기를 작성해 JSON 객체로 반환하세요.

## 도서 목록
{json.dumps(books_spec, ensure_ascii=False, indent=2)}

## 작성 규칙 (반드시 준수)
1. 각 도서의 `age_guide`와 줄거리/소재에 100% 맞게 작성 (초등 도서에 어린이집/배변/보드북 등 영아 소재 절대 금지).
2. 줄거리 요약 금지. 부모가 읽어주었을 때 아이의 반응·대화·변화에 집중.
3. 길이와 문체 다양화:
   - 각 도서 리뷰 중 일부는 15~30자 짧은 솔직 한 줄 평 ("아이가 매일 꺼내봐요", "강추요~", "그림이 예뻐서 좋아해요ㅎㅎ" 등)
   - 나머지는 35~70자 자연스러운 구어체 1~2문장. AI 특유의 딱딱한 정리 문체("~하는 책입니다. 읽어보세요.") 금지.
4. `rating`: 4.0~5.0 사이 숫자, `selected_badges`: 아래 10종 중 1~3개 정확히 선택.

## 선택 가능한 뱃지 10종
{json.dumps(BADGE_LIST, ensure_ascii=False)}

## 출력 형식 (순수 JSON 객체만 반환, 키는 문자열 book_id)
```json
{{
  "1234": [
    {{
      "rating": 5.0,
      "child_age": "6세",
      "selected_badges": ["⭐ 우리 아이 최애 책이에요"],
      "content": "후기 내용..."
    }}
  ]
}}
```"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    parsed = json.loads(text)
    result: Dict[int, List[dict]] = {}
    for k, v in parsed.items():
        if isinstance(v, list):
            result[int(k)] = v
    return result


def process_single_book(
    idx: int,
    total: int,
    book: dict,
    existing_cnt: int,
    existing_nicks: Set[str],
    min_reviews: int,
    max_reviews: int,
) -> Tuple[bool, int, str]:
    book_id = book["id"]
    title = book.get("title", f"ID:{book_id}")
    target_total = random.randint(min_reviews, max_reviews)
    needed = max(1, target_total - existing_cnt)

    book_for_prompt = dict(book)
    if not book_for_prompt.get("age") and "초등" in (book_for_prompt.get("curation_tag") or ""):
        book_for_prompt["age"] = "8-12"

    logger.info(
        f"[{idx}/{total}] '{title}' (ID:{book_id}, 연령:{book_for_prompt.get('age')}, 기존:{existing_cnt}개) — {needed}개 생성 중 (목표 {target_total}개)..."
    )

    reviews = None
    for attempt in range(3):
        reviews = generate_reviews_for_book(book_for_prompt, count=needed)
        if reviews:
            break
        wait = 2.0 * (attempt + 1)
        logger.warning(f"  [{title}] 생성 재시도 ({attempt + 1}/3) — {wait}초 대기")
        time.sleep(wait)

    if not reviews:
        logger.error(f"  ❌ [{title}] Gemini 생성 최종 실패")
        return False, 0, title

    inserted = insert_reviews_safe(book_id, title, reviews, existing_nicks)
    if inserted > 0:
        logger.info(f"  ✅ [{title}] {inserted}개 적재 완료 (총 {existing_cnt + inserted}개)")
        return True, inserted, title
    else:
        logger.error(f"  ❌ [{title}] DB 삽입 실패")
        return False, 0, title


def main():
    parser = argparse.ArgumentParser(description="홈 화면 노출 도서 시드 리뷰(2~4개) 생성")
    parser.add_argument("--dry-run", action="store_true", help="DB 삽입 없이 대상 도서 및 현황만 확인")
    parser.add_argument("--min-reviews", type=int, default=2, help="도서당 최소 리뷰 개수 (기본 2)")
    parser.add_argument("--max-reviews", type=int, default=4, help="도서당 최대 리뷰 개수 (기본 4)")
    parser.add_argument("--initial-only", action="store_true", help="탭 클릭 없이 최초 홈 로드 노출 도서만 대상")
    parser.add_argument("--workers", type=int, default=4, help="병렬 처리 워커 수 (기본 4)")
    parser.add_argument("--batch-size", type=int, default=10, help="1회 API 호출당 묶을 도서 수 (기본 10)")
    parser.add_argument("--model", type=str, default=None, help="특정 Gemini 모델 지정 (미지정 시 자동 폴백)")
    args = parser.parse_args()

    if not args.dry_run and not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    now_kst = get_kst_now()
    logger.info(f"=== 홈 화면 노출 도서 리뷰 생성 시작 (KST: {now_kst.strftime('%Y-%m-%d %H:%M')}) ===")

    # 1. 기존 리뷰 현황 수집
    reviews_map = get_existing_reviews_map()
    logger.info(f"DB 내 기존 리뷰가 있는 도서: {len(reviews_map)}권")

    # 2. 홈 화면 섹션별 도서 수집
    books_map: Dict[int, dict] = {}

    def collect(section_name: str, books: List[dict]):
        need = sum(1 for b in books if len(reviews_map.get(b["id"], [])) < args.min_reviews)
        logger.info(f"  [{section_name}] {len(books)}권 조회 (2개 미만: {need}권)")
        for b in books:
            books_map[b["id"]] = b

    # 2-1. 이번 주 AI 주간 큐레이션
    for name, tag in get_weekly_curation_tags(now_kst):
        collect(name, fetch_books_by_tag(tag, 14))

    # 2-2. 50+ 전문 테마 큐레이션 쇼케이스
    theme_tabs = POPULAR_THEME_TAGS[:1] if args.initial_only else POPULAR_THEME_TAGS
    for name, tag in theme_tabs:
        collect(name, fetch_books_by_tag(tag, 14))

    # 2-3. 2022 개정 교과서 수록도서 쇼케이스
    textbook_tabs = TEXTBOOK_GRADE_TAGS[:1] if args.initial_only else TEXTBOOK_GRADE_TAGS
    for name, grade_tag in textbook_tabs:
        collect(name, fetch_textbook_books(grade_tag, 6, now_kst))

    # 2-4. 칼데콧 수상작
    collect("칼데콧 수상작", fetch_caldecott_books(14))

    # 2-5. 어린이도서연구회 추천
    collect("어린이도서연구회 추천", fetch_research_council_books(14, now_kst))

    all_home_books = list(books_map.values())
    logger.info(f"\n홈 노출 도서 총계 (중복 제거): {len(all_home_books)}권")

    # 3. 최소 리뷰 수(2개) 미만 도서 필터링
    target_books = []
    for b in all_home_books:
        existing_cnt = len(reviews_map.get(b["id"], []))
        if existing_cnt < args.min_reviews:
            target_books.append((b, existing_cnt))

    already_ok = len(all_home_books) - len(target_books)
    logger.info(f"이미 {args.min_reviews}개 이상 보유: {already_ok}권 | 추가 생성 필요: {len(target_books)}권")

    if not target_books:
        logger.info(f"✅ 모든 홈 노출 도서에 이미 {args.min_reviews}개 이상의 댓글이 달려 있습니다!")
        return

    if args.dry_run:
        logger.info("\n[DRY RUN] 생성 대상 도서 목록:")
        for b, cnt in target_books:
            logger.info(f"  - ID {b['id']}: {b['title']} (연령: {b.get('age')}, 현재 리뷰: {cnt}개)")
        return

    # 4. 리뷰 생성 & 삽입 (배치 처리 + 모델 자동 폴백)
    success = 0
    fail = 0
    total_inserted = 0
    failed_titles = []

    models_to_try = [args.model] if args.model else list(MODEL_FALLBACK_LIST)
    model_idx = 0

    # 각 도서별 목표 생성 개수 사전 결정
    planned_items = []
    for book, existing_cnt in target_books:
        target_total = random.randint(args.min_reviews, args.max_reviews)
        needed = max(1, target_total - existing_cnt)
        planned_items.append((book, existing_cnt, needed, target_total))

    batch_size = max(1, args.batch_size)
    batches = [planned_items[i : i + batch_size] for i in range(0, len(planned_items), batch_size)]
    logger.info(f"총 {len(planned_items)}권을 {len(batches)}개 배치(배치당 최대 {batch_size}권)로 처리합니다.")

    for b_idx, batch in enumerate(batches, 1):
        batch_input = [(book, needed) for book, _, needed, _ in batch]
        batch_result = None

        while model_idx < len(models_to_try):
            cur_model = models_to_try[model_idx]
            try:
                logger.info(f"[배치 {b_idx}/{len(batches)}] {len(batch)}권 생성 중 (모델: {cur_model})...")
                batch_result = generate_reviews_batch(batch_input, cur_model)
                break
            except Exception as e:
                err_str = str(e)
                logger.warning(f"  [배치 {b_idx}] 모델 {cur_model} 실패: {err_str[:200]}")
                if "429" in err_str or "404" in err_str or "quota" in err_str.lower() or "not found" in err_str.lower():
                    model_idx += 1
                    logger.info(f"  다음 모델로 전환 시도 ({model_idx}/{len(models_to_try)})...")
                    time.sleep(1.0)
                else:
                    time.sleep(2.0)
                    # JSON 파싱 오류 등 일시 오류면 1회 재시도 후 모델 전환
                    try:
                        batch_result = generate_reviews_batch(batch_input, cur_model)
                        break
                    except Exception as e2:
                        logger.error(f"  [배치 {b_idx}] 재시도 실패: {e2}")
                        break

        if not batch_result:
            for book, _, _, _ in batch:
                fail += 1
                failed_titles.append(book.get("title", str(book["id"])))
            continue

        for book, existing_cnt, needed, target_total in batch:
            book_id = book["id"]
            title = book.get("title", f"ID:{book_id}")
            reviews = batch_result.get(book_id, [])[:needed]
            if not reviews:
                logger.warning(f"  ⚠️ [{title}] 응답 누락")
                fail += 1
                failed_titles.append(title)
                continue

            existing_nicks = set(reviews_map.get(book_id, []))
            inserted = insert_reviews_safe(book_id, title, reviews, existing_nicks)
            if inserted > 0:
                logger.info(f"  ✅ [{title}] {inserted}개 적재 완료 (총 {existing_cnt + inserted}개)")
                total_inserted += inserted
                success += 1
            else:
                fail += 1
                failed_titles.append(title)

        time.sleep(1.5)

    logger.info("\n=== 완료 ===")
    logger.info(f"성공: {success}권 | 실패: {fail}권 | 총 신규 댓글 적재: {total_inserted}개")
    if failed_titles:
        logger.warning(f"실패 도서: {', '.join(failed_titles)}")

    # 5. 최종 커버리지 검증
    reviews_map_after = get_existing_reviews_map()
    covered = sum(1 for b in all_home_books if len(reviews_map_after.get(b["id"], [])) >= args.min_reviews)
    logger.info(
        f"홈 노출 도서 {args.min_reviews}개+ 댓글 커버리지: {covered}/{len(all_home_books)}권 ({covered / len(all_home_books) * 100:.1f}%)"
    )


if __name__ == "__main__":
    main()
