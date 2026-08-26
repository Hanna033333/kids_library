"""
AI 시드 리뷰 자동 생성 스크립트
Gemini API를 활용하여 도서당 3~5개의 3040 부모 생생한 구어체 후기,
평점(4.0~5.0), 범용 10종 뱃지 선택 데이터를 자동 생성 및 DB 적재
"""
import os
import sys
import json
import time
import random
from typing import Optional, List
import logging

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Supabase 클라이언트
# ──────────────────────────────────────────────
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ──────────────────────────────────────────────
# 범용 10종 뱃지 (백엔드 API와 동일하게 유지)
# ──────────────────────────────────────────────
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

# ──────────────────────────────────────────────
# 닉네임 풀 (형용사+명사 회원가입 브랜드 닉네임 정책)
# ──────────────────────────────────────────────
NICKNAME_POOL = [
    "지혜로운책벌레", "따스한책부엉이", "포근한책요정", "정겨운글벗", "행복한독서가",
    "다정한이야기꾼", "꿈꾸는파랑새", "다독이는책탐험가", "슬기로운책마을님", "다복한글나무",
    "마음넓은책나무", "빛나는책벌레", "샘깊은책부엉이", "글사랑책요정", "봄날의글벗",
    "지혜로운이야기꾼", "따스한독서가", "포근한파랑새", "정겨운책탐험가", "행복한책마을님",
    "다정한글나무", "꿈꾸는책나무", "다독이는책벌레", "슬기로운책부엉이", "다복한책요정",
    "마음넓은글벗", "빛나는독서가", "샘깊은이야기꾼", "글사랑파랑새", "봄날의책탐험가",
    "지혜로운책마을님", "따스한글나무", "포근한책나무", "정겨운책벌레", "행복한책부엉이",
    "다정한책요정", "꿈꾸는글벗", "다독이는독서가", "슬기로운이야기꾼", "다복한파랑새",
]


def generate_reviews_for_book(book: dict, count: int = 4) -> Optional[List[dict]]:
    """Gemini API를 사용하여 단일 도서의 시드 리뷰 지정된 개수(count)만큼 생성"""
    import google.generativeai as genai
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    title = book.get("title", "")
    author = book.get("author", "")
    age = book.get("age", "")
    category = book.get("category", "")
    curation_tag = book.get("curation_tag", "")
    description = (book.get("description") or "정보 없음")[:300]

    prompt = f"""당신은 3040 한국 부모님들의 진짜 육아 경험을 담아 생생한 도서 후기를 작성하는 전문가입니다.
다음 어린이 도서의 주제/줄거리 맥락에 연관하여, 부모가 이 책을 들인 이유와 아이의 반응이 담긴 후기 {count}개를 JSON 배열로 생성해주세요.

## 도서 정보
- 제목: {title}
- 저자: {author}
- 연령: {age}
- 카테고리: {category}
- 큐레이션 태그: {curation_tag}
- 책 줄거리/소재 참고: {description}

## 핵심 작성 규칙 (반드시 엄수)
1. **줄거리 직접 요약 금지 & 줄거리 맥락 연관 (최우선)**:
   - ❌ 리뷰에 책 줄거리나 스포일러를 억지로 설명하거나 요약하지 마세요. (예: "이 책은 주인공이 소금이 나오는 맷돌을 바다에 빠뜨린 이야기입니다" - 금지)
   - ⭕ 대신 **이 책의 줄거리/소재/주제(예: 탐욕, 거짓말, 어둠, 떼쓰기, 우정 등 책 내용의 맥락)**와 **자연스럽게 연관된 실제 부모의 육아 고민이나 선택 이유, 아이의 반응**을 써주세요.
2. **단편 후기 지양**:
   - 단순히 "좋아요", "잘 봐요" 같은 단순 한줄평보다는 80~160자 분량으로 실제 부모의 구체적 맥락이 담기도록 하세요.
3. **톤앤매너**: 3040 부모의 솔직한 구어체 (예: "반신반의하며 들였는데 대성공", "아이 마음 다독여주기 딱이에요", "요즘 최애 책 됐어요 ㅋㅋ")
4. 각 리뷰마다 rating(4.0~5.0 사이 소수점 1자리), selected_badges(아래 10종 중 1~3개 선택), content(후기 본문)를 포함하세요.
5. child_age는 도서 연령에 맞춰 "2세"~"8세" 등으로 자연스럽게 배분하세요.

## 선택 가능한 뱃지 10종 (이 목록에서만 선택)
{json.dumps(BADGE_LIST, ensure_ascii=False)}

## 출력 형식 (JSON 배열만 반환, 다른 텍스트 금지)
```json
[
  {{
    "rating": 5.0,
    "child_age": "5세",
    "selected_badges": ["💡 새로운 상상력을 자극해요", "⭐ 우리 아이 최애 책이에요"],
    "content": "후기 내용..."
  }}
]
```"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # JSON 파싱 (코드블록 제거)
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        reviews = json.loads(text)
        
        if not isinstance(reviews, list):
            logger.warning(f"[{title}] 생성 결과가 배열이 아님: {type(reviews)}")
            return None
        
        return reviews[:count]
    except Exception as e:
        logger.error(f"[{title}] Gemini API 호출 실패: {e}")
        return None


def insert_reviews(book_id: int, book_title: str, reviews: List[dict]):
    """생성된 리뷰를 DB에 삽입 — 성공한 삽입 수 반환"""
    used_nicknames = set()
    inserted = 0
    
    for review in reviews:
        # 닉네임 중복 방지
        nickname = random.choice([n for n in NICKNAME_POOL if n not in used_nicknames] or NICKNAME_POOL)
        used_nicknames.add(nickname)
        
        # 뱃지 유효성 검증
        selected_badges = [b for b in review.get("selected_badges", []) if b in BADGE_LIST]
        
        # 난수 생성 시각 (최근 60일 내 분산)
        days_ago = random.randint(1, 60)
        hours_ago = random.randint(0, 23)
        created_at_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - (days_ago * 86400 + hours_ago * 3600)))

        # 1. 신규 스키마 컬럼으로 시도
        data_new = {
            "book_id": book_id,
            "nickname": nickname,
            "child_age": review.get("child_age"),
            "rating": min(5.0, max(1.0, float(review.get("rating", 4.5)))),
            "selected_badges": selected_badges,
            "content": review.get("content", "")[:500],
            "created_at": created_at_time,
            "is_ai_generated": True,
        }
        
        try:
            result = supabase.table("book_reviews").insert(data_new).execute()
            if result.data:
                inserted += 1
            else:
                raise Exception("New schema insert empty response")
        except Exception as e:
            # 2. 레가시 스키마 (comment, rating, book_id, created_at)로 안전 폴백
            badges_str = ", ".join(selected_badges) if selected_badges else ""
            age_str = f"[{review.get('child_age')}] " if review.get('child_age') else ""
            badge_prefix = f"({badges_str}) " if badges_str else ""
            
            full_comment = f"{nickname}님 {age_str}{badge_prefix}{review.get('content', '')}"
            
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
                logger.error(f"[{book_title}] 리뷰 레가시 삽입도 실패: {e2}")
    
    return inserted


def main():
    """홈 화면 큐레이션 및 대표 인기 도서 50권에 대해 불균등 시드 리뷰 생성 및 적재"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI 시드 리뷰 자동 생성")
    parser.add_argument("--limit", type=int, default=50, help="처리할 도서 수 제한 (기본값: 50권)")
    parser.add_argument("--skip-existing", action="store_true", default=False, help="이미 리뷰가 있는 도서 건너뛰기")
    parser.add_argument("--dry-run", action="store_true", help="DB 삽입 없이 생성만 테스트")
    args = parser.parse_args()
    
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # 큐레이션 도서 및 인기 도서 목록 조회
    logger.info("큐레이션 및 인기 도서 목록 조회 중...")
    result = supabase.table("childbook_items")\
        .select("id, title, author, age, category, curation_tag, national_loan_count")\
        .not_.is_("curation_tag", "null")\
        .order("national_loan_count", desc=True)\
        .limit(args.limit)\
        .execute()
    
    books = result.data or []
    
    # 큐레이션 도서가 50권 미만일 경우 일반 인기 도서 보충
    if len(books) < args.limit:
        needed = args.limit - len(books)
        existing_ids = [b["id"] for b in books]
        more_res = supabase.table("childbook_items")\
            .select("id, title, author, age, category, curation_tag, national_loan_count")\
            .not_.in_("id", existing_ids)\
            .order("national_loan_count", desc=True)\
            .limit(needed)\
            .execute()
        if more_res.data:
            books.extend(more_res.data)

    logger.info(f"타겟 도서: 총 {len(books)}권 선별 완료")
    
    success_count = 0
    fail_count = 0
    total_inserted = 0
    
    for i, book in enumerate(books, 1):
        book_id = book["id"]
        title = book.get("title", f"ID:{book_id}")
        
        # 불균등 수량 배분: 상위 15권은 5~6개, 나머지 35권은 2~3개 생성
        if i <= 15:
            target_review_count = random.randint(5, 6)
        else:
            target_review_count = random.randint(2, 3)
            
        logger.info(f"[{i}/{len(books)}] {title} 리뷰 {target_review_count}개 생성 중...")
        
        reviews = generate_reviews_for_book(book, count=target_review_count)
        
        if not reviews:
            fail_count += 1
            continue
        
        if args.dry_run:
            logger.info(f"  [DRY RUN] 생성된 리뷰 {len(reviews)}개:")
            for r in reviews:
                logger.info(f"    ⭐{r.get('rating')} | {r.get('content', '')[:60]}...")
            success_count += 1
        else:
            inserted = insert_reviews(book_id, title, reviews)
            if inserted > 0:
                logger.info(f"  ✅ {inserted}/{len(reviews)}개 리뷰 DB 적재 완료")
                total_inserted += inserted
                success_count += 1
            else:
                logger.error(f"  ❌ [{title}] 모든 리뷰 삽입 실패")
                fail_count += 1
        
        # API Rate Limit 방지
        time.sleep(1.2)
    
    logger.info(f"\n===== 시드 리뷰 적재 작업 완료 =====")
    logger.info(f"성공 도서: {success_count}권 | 실패: {fail_count}권 | 총 생성 및 적재된 리뷰: {total_inserted}개")


if __name__ == "__main__":
    main()
