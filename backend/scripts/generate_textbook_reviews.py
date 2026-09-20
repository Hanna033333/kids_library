"""
교과서 수록 도서 AI 시드 리뷰 자동 생성 스크립트
- 교과서 수록 도서(~212권) 중 약 70% 대상
- 도서당 1~3개의 리뷰를 랜덤하게 생성
- 초등 학년별 맥락(교과서 연계, 국어 수업, 어휘/문해력, 학교생활 등)에 부합하는 자연스러운 부모 후기 생성
"""
import os
import sys
import json
import time
import random
import re
from typing import Optional, List, Dict
import logging

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY
from supabase import create_client
import google.generativeai as genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Supabase 클라이언트 (서비스 키 우선 사용)
client_key = SUPABASE_SERVICE_KEY or SUPABASE_KEY
supabase = create_client(SUPABASE_URL, client_key)

# 범용 10종 뱃지
BADGE_LIST = [
    "🎨 그림체가 좋아요",
    "😆 깔깔 웃으며 무한 반복 요청해요",
    "📖 글밥이 적당해요",
    "🧠 호기심이 부쩍 늘었어요",
    "⭐ 우리 아이 최애 책이에요",
    "💬 아이와 대화거리가 풍부해져요",
    "💡 새로운 상상력을 자극해요",
    "📚 꼭 읽어볼 만해요",
    "☀️ 아이 혼자서도 잘 펼쳐봐요",
    "👏 아이 집중력이 엄청 높아져요",
]

# 닉네임 풀
NICKNAME_POOL = [
    "지혜로운책벌레", "따스한책부엉이", "포근한책요정", "정겨운글벗", "행복한독서가",
    "다정한이야기꾼", "꿈꾸는파랑새", "다독이는책탐험가", "슬기로운책마을님", "다복한글나무",
    "마음넓은책나무", "빛나는책벌레", "샘깊은책부엉이", "글사랑책요정", "봄날의글벗",
    "지혜로운이야기꾼", "따스한독서가", "포근한파랑새", "정겨운책탐험가", "행복한책마을님",
    "다정한글나무", "꿈꾸는책나무", "다독이는책벌레", "슬기로운책부엉이", "다복한책요정",
    "마음넓은글벗", "빛나는독서가", "샘깊은이야기꾼", "글사랑파랑새", "봄날의책탐험가",
    "지혜로운책마을님", "따스한글나무", "포근한책나무", "정겨운책벌레", "행복한책부엉이",
    "다정한책요정", "꿈꾸는글벗", "다독이는독서가", "슬기로운이야기꾼", "다복한파랑새",
    "은빛독서가", "푸른나무글벗", "별빛책사랑", "달빛글마루", "솔바람책벗",
    "늘푸른독서맘", "초록잎책이야기", "책읽는나무", "아이사랑글방", "배움가득부엉이"
]


def extract_grade_info(curation_tag: str) -> str:
    """curation_tag에서 학년 정보 추출 (예: #초등1학년 -> 초등 1학년)"""
    if not curation_tag:
        return "초등학교"
    for grade in ["1학년", "2학년", "3학년", "4학년", "5학년", "6학년"]:
        if grade in curation_tag:
            return f"초등 {grade}"
    return "초등 전학년"


def get_child_age_candidates(grade_info: str) -> List[str]:
    """학년에 맞는 child_age 후보 반환"""
    if "1학년" in grade_info:
        return ["초등1", "8세", "8세", "초등1학년"]
    elif "2학년" in grade_info:
        return ["초등2", "9세", "9세", "초등2학년"]
    elif "3학년" in grade_info:
        return ["초등3", "10세", "10세", "초등3학년"]
    elif "4학년" in grade_info:
        return ["초등4", "11세", "11세", "초등4학년"]
    elif "5학년" in grade_info:
        return ["초등5", "12세", "12세", "초등5학년"]
    elif "6학년" in grade_info:
        return ["초등6", "13세", "13세", "초등6학년"]
    return ["초등1", "초등2", "초등3", "초등4", "8세", "9세", "10세"]


def generate_reviews_for_textbook(model, book: dict, count: int) -> Optional[List[dict]]:
    """Gemini API를 사용하여 교과서 수록 도서의 시드 리뷰 생성"""
    title = book.get("title", "")
    author = book.get("author", "")
    curation_tag = book.get("curation_tag", "")
    category = book.get("category", "")
    description = (book.get("description") or "정보 없음")[:400]
    grade_info = extract_grade_info(curation_tag)
    child_age_options = get_child_age_candidates(grade_info)

    prompt = f"""당신은 초등학생 자녀를 둔 3040 학부모들이 남기는 실제 도서 후기를 작성하는 전문가입니다.
초등학교 국어 교과서에 수록된 다음 도서에 대해, 실제 학부모들의 생생하고 자연스러운 후기 {count}개를 JSON 배열로 생성해주세요.

## 도서 정보
- 제목: {title}
- 저자: {author}
- 교과서 수록 학년: {grade_info}
- 카테고리/태그: {curation_tag}
- 책 줄거리/소재: {description}

## 후기 작성 지침
1. **대상 연령 & 학년 일치 (최우선)**:
   - 이 책은 **{grade_info}** 국어 교과서 수록 도서입니다.
   - `child_age`는 {json.dumps(child_age_options, ensure_ascii=False)} 중에서 적절히 선택하세요.
   - 🚨 **[절대 금지]**: 0~4세 아기 관련 소재(배변 훈련, 아기 젖병, 옹알이, 어린이집 등원, 보드북 등)는 절대 사용하지 마세요.
2. **초등 교과서 수록 도서다운 자연스러운 계기와 반응**:
   - 국어 교과서에 나와서 아이가 학교에서 배우고 와서 반가워하며 전체 책을 찾아 읽음
   - 수업 예습/복습용으로 읽혔는데 글밥도 적당하고 독해력/어휘력에 도움됨
   - 학교 도서관이나 집에서 읽고 독서록/독서기록장 쓸 때 좋은 생각거리가 됨
   - 친구 관계, 배려, 상상력, 감정 표현 등 초등 시기 아이 마음에 와닿는 이야기
   - 단, 모든 후기가 교과서 이야기만 하면 부자연스러우므로, 책 자체의 재미/감동에 대한 일반 초등 독서 후기도 섞어주세요.
3. **길이와 문체 다양화**:
   - {count}개 중 1개는 **짧고 직관적인 한 줄 평** (15~30자)
     (예: "교과서에 나온다고 해서 빌려봤는데 아이가 재미있게 잘 읽네요", "글밥 적당하고 초등 아이 읽기 딱 좋아요", "학교 수업 듣고 와서 찾아서 다시 읽었어요", "아이가 너무 재밌어해요 추천합니다")
   - 나머지는 **1~2문장의 자연스러운 구어체** (40~75자)
     (예: "국어 시간에 일부만 읽고 와서 뒷이야기가 궁금하다고 해서 빌려줬어요. 끝까지 집중해서 단숨에 다 읽네요 ㅎㅎ", "교과서 수록작이라 믿고 골랐는데 그림도 예쁘고 아이랑 학교 이야기 나누기 참 좋았습니다.")
   - **기계적이거나 딱딱한 교과서 해설체 절대 금지**.
4. **필드 규격**:
   - `rating`: 4.0, 4.5, 5.0 중 하나 (대부분 5.0 또는 4.5)
   - `child_age`: 위 학년 후보 중 하나
   - `selected_badges`: 아래 10종 뱃지 중 1~2개 선택
   - `content`: 후기 본문

## 선택 가능한 뱃지 목록
{json.dumps(BADGE_LIST, ensure_ascii=False)}

## 출력 형식 (JSON 배열만 출력)
```json
[
  {{
    "rating": 5.0,
    "child_age": "{child_age_options[0]}",
    "selected_badges": ["📖 글밥이 적당해요", "📚 꼭 읽어볼 만해요"],
    "content": "후기 내용..."
  }}
]
```"""

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            reviews = json.loads(text)
            if isinstance(reviews, list) and len(reviews) > 0:
                return reviews[:count]
        except Exception as e:
            logger.warning(f"[{title}] 생성 시도 {attempt+1} 실패: {e}")
            time.sleep(1.5)

    return None


def insert_reviews(book_id: int, book_title: str, reviews: List[dict]) -> int:
    """리뷰를 DB에 삽입"""
    used_nicknames = set()
    inserted = 0

    for review in reviews:
        avail_nicks = [n for n in NICKNAME_POOL if n not in used_nicknames] or NICKNAME_POOL
        nickname = random.choice(avail_nicks)
        used_nicknames.add(nickname)

        selected_badges = [b for b in review.get("selected_badges", []) if b in BADGE_LIST]
        days_ago = random.randint(1, 50)
        hours_ago = random.randint(0, 23)
        created_at_time = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(time.time() - (days_ago * 86400 + hours_ago * 3600))
        )

        content_text = review.get("content", "").strip()[:500]
        if not content_text:
            continue

        data_new = {
            "book_id": book_id,
            "nickname": nickname,
            "child_age": review.get("child_age", "초등"),
            "rating": int(round(min(5.0, max(1.0, float(review.get("rating", 5.0)))))),
            "selected_badges": selected_badges,
            "content": content_text,
            "comment": content_text,  # NOT NULL 충족
            "created_at": created_at_time,
            "is_ai_generated": True,
        }

        try:
            result = supabase.table("book_reviews").insert(data_new).execute()
            if result.data:
                inserted += 1
            else:
                raise Exception("Empty insert response")
        except Exception as e:
            logger.warning(f"[{book_title}] 신규 스키마 삽입 실패 ({e}), 레가시 폴백 시도")
            badges_str = ", ".join(selected_badges) if selected_badges else ""
            age_str = f"[{review.get('child_age')}] " if review.get('child_age') else ""
            badge_prefix = f"({badges_str}) " if badges_str else ""
            full_comment = f"{nickname}님 {age_str}{badge_prefix}{content_text}"

            data_legacy = {
                "book_id": book_id,
                "rating": int(review.get("rating", 5)),
                "comment": full_comment[:500],
                "created_at": created_at_time,
            }
            try:
                result = supabase.table("book_reviews").insert(data_legacy).execute()
                if result.data:
                    inserted += 1
            except Exception as e2:
                logger.error(f"[{book_title}] 레가시 삽입도 실패: {e2}")

    return inserted


def main():
    import argparse
    parser = argparse.ArgumentParser(description="교과서 수록 도서 리뷰 생성")
    parser.add_argument("--ratio", type=float, default=0.70, help="리뷰를 작성할 도서 비율 (기본값: 0.70 = 70%)")
    parser.add_argument("--dry-run", action="store_true", help="DB 삽입 없이 테스트")
    args = parser.parse_args()

    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    genai.configure(api_key=GEMINI_API_KEY)
    # gemini-2.5-flash 모델 초기화
    model = genai.GenerativeModel("gemini-2.5-flash")

    logger.info("=== 교과서 수록 도서 리뷰 생성 시작 ===")
    
    # 1. 전체 교과서 수록 도서 조회
    fields = "id, title, author, age, category, curation_tag, national_loan_count, description"
    res = supabase.table("childbook_items").select(fields).ilike("curation_tag", "%교과서수록%").order("national_loan_count", desc=True).execute()
    all_textbooks = res.data or []
    total_count = len(all_textbooks)
    logger.info(f"총 교과서 수록 도서: {total_count}권")

    # 2. 이미 리뷰가 있는 도서 확인
    all_book_ids = [b["id"] for b in all_textbooks]
    review_res = supabase.table("book_reviews").select("id, book_id").in_("book_id", all_book_ids).execute()
    reviewed_ids = set(r["book_id"] for r in (review_res.data or []))
    logger.info(f"이미 리뷰가 존재하는 교과서 도서: {len(reviewed_ids)}권")

    # 3. 목표 대상 권수 계산 (전체의 약 70%)
    target_total = int(round(total_count * args.ratio))  # ~148권
    logger.info(f"목표 리뷰 도서 권수 (전체 {total_count}권의 {int(args.ratio*100)}%): {target_total}권")

    # 아직 리뷰가 없는 도서 리스트
    unreviewed_books = [b for b in all_textbooks if b["id"] not in reviewed_ids]
    needed_count = max(0, target_total - len(reviewed_ids))
    logger.info(f"신규 리뷰 작성이 필요한 도서: {needed_count}권 (미작성 후보: {len(unreviewed_books)}권)")

    if needed_count == 0:
        logger.info("이미 목표 비율 이상의 교과서 도서에 리뷰가 있습니다.")
        return

    # 학년별 고른 분포를 위해 학년별로 분류 후 균등 샘플링
    grade_groups: Dict[str, List[dict]] = {}
    for b in unreviewed_books:
        g = extract_grade_info(b.get("curation_tag", ""))
        grade_groups.setdefault(g, []).append(b)

    selected_books = []
    # 각 학년별로 일정 비율씩 균등하게 선별
    for grade, g_books in grade_groups.items():
        g_needed = max(1, int(round(len(g_books) * args.ratio)))
        # 대출수 상위 도서와 랜덤 도서를 적절히 혼합
        # 상위 40%는 대출순 고정, 나머지는 무작위 샘플
        g_books_sorted = sorted(g_books, key=lambda x: x.get("national_loan_count") or 0, reverse=True)
        top_split = max(1, int(g_needed * 0.4))
        top_books = g_books_sorted[:top_split]
        remaining_books = g_books_sorted[top_split:]
        
        sample_size = min(len(remaining_books), g_needed - len(top_books))
        if sample_size > 0:
            random_sample = random.sample(remaining_books, sample_size)
        else:
            random_sample = []
            
        selected_for_grade = top_books + random_sample
        selected_books.extend(selected_for_grade)
        logger.info(f"  - [{grade}] 전체 {len(g_books)}권 중 {len(selected_for_grade)}권 선별")

    # 전체 목표 수치(needed_count)와 맞추기 위해 조정
    if len(selected_books) > needed_count:
        random.shuffle(selected_books)
        selected_books = selected_books[:needed_count]
    elif len(selected_books) < needed_count:
        already_selected_ids = set(b["id"] for b in selected_books)
        leftover = [b for b in unreviewed_books if b["id"] not in already_selected_ids]
        add_cnt = min(len(leftover), needed_count - len(selected_books))
        if add_cnt > 0:
            selected_books.extend(random.sample(leftover, add_cnt))

    logger.info(f"\n최종 선별된 신규 작업 대상 도서: {len(selected_books)}권")

    # 4. 리뷰 개수 1~3개 랜덤 할당
    # 가중치: 1개: 35%, 2개: 45%, 3개: 20%
    review_counts = random.choices([1, 2, 3], weights=[35, 45, 20], k=len(selected_books))

    success_books = 0
    fail_books = 0
    total_reviews_inserted = 0

    for idx, (book, r_count) in enumerate(zip(selected_books, review_counts), 1):
        book_id = book["id"]
        title = book.get("title", f"ID:{book_id}")
        grade = extract_grade_info(book.get("curation_tag", ""))

        logger.info(f"[{idx}/{len(selected_books)}] '{title}' ({grade}) -> 리뷰 {r_count}개 생성 요청...")

        reviews = generate_reviews_for_textbook(model, book, count=r_count)
        if not reviews:
            logger.error(f"  ❌ [{title}] 리뷰 생성 실패")
            fail_books += 1
            time.sleep(1.0)
            continue

        if args.dry_run:
            logger.info(f"  [DRY RUN] 생성 성공 ({len(reviews)}개):")
            for r in reviews:
                logger.info(f"    ⭐ {r.get('rating')} | [{r.get('child_age')}] {r.get('content')}")
            success_books += 1
            total_reviews_inserted += len(reviews)
        else:
            inserted = insert_reviews(book_id, title, reviews)
            if inserted > 0:
                logger.info(f"  ✅ {inserted}/{len(reviews)}개 리뷰 DB 적재 완료")
                success_books += 1
                total_reviews_inserted += inserted
            else:
                logger.error(f"  ❌ [{title}] DB 적재 실패")
                fail_books += 1

        # API Rate Limit 안전 딜레이
        time.sleep(0.8)

    logger.info("\n" + "="*50)
    logger.info("교과서 수록 도서 리뷰 적재 완료 보고")
    logger.info(f"- 전체 교과서 도서: {total_count}권")
    logger.info(f"- 성공 도서 수: {success_books}권 (실패: {fail_books}권)")
    logger.info(f"- 신규 적재된 총 리뷰 수: {total_reviews_inserted}개")
    final_reviewed_count = len(reviewed_ids) + success_books
    logger.info(f"- 리뷰 보유 교과서 도서: {final_reviewed_count}/{total_count}권 ({final_reviewed_count/total_count*100:.1f}%)")
    logger.info("="*50)


if __name__ == "__main__":
    main()
