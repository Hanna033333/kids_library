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
    "⭐ 매일 밤 가져오는 최애 책이에요",
    "💬 아이와 대화거리가 풍부해져요",
    "💡 새로운 상상력을 자극해요",
    "📚 도서관에서 꼭 빌려볼 만해요",
    "☀️ 아이 혼자서도 잘 펼쳐봐요",
    "👏 아이 집중력이 엄청 높아져요",
]

# ──────────────────────────────────────────────
# 닉네임 풀 (자연스러운 부모 닉네임)
# ──────────────────────────────────────────────
NICKNAME_POOL = [
    "서아맘", "지후아빠", "하윤맘", "도윤이네", "시우맘",
    "예은맘", "지안이아빠", "수아네", "하람맘", "시연맘",
    "채원이네", "민준아빠", "소율맘", "현우아빠", "다은이네",
    "윤서맘", "지호아빠", "은우맘", "서준이네", "유나맘",
    "태오아빠", "하린맘", "건우아빠", "소민이네", "예린맘",
    "시현맘", "주원이네", "나윤맘", "도현아빠", "서윤이네",
]


def generate_reviews_for_book(book: dict) -> Optional[List[dict]]:
    """Gemini API를 사용하여 단일 도서의 시드 리뷰 3~5개 생성"""
    import google.generativeai as genai
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    title = book.get("title", "")
    author = book.get("author", "")
    age = book.get("age", "")
    category = book.get("category", "")
    curation_tag = book.get("curation_tag", "")

    prompt = f"""당신은 3040 한국 부모님들의 진짜 육아 후기를 작성하는 전문가입니다.
다음 어린이 도서에 대해 실제 부모가 쓴 것처럼 자연스럽고 생생한 한줄평 리뷰 4개를 JSON 배열로 생성해주세요.

## 도서 정보
- 제목: {title}
- 저자: {author}
- 연령: {age}
- 카테고리: {category}
- 큐레이션 태그: {curation_tag}

## 반드시 지켜야 할 규칙
1. 톤앤매너: 3040 부모의 실제 구어체 (예: "우리 아이 완전 좋아해요", "ㅋㅋ 매일 읽어달라고 가져와요", "목이 쉬도록 읽어줬어요 😭")
2. 각 리뷰마다 rating(4.0~5.0 사이 소수점 1자리), selected_badges(아래 10종 중 1~3개 선택), content(30~80자 한줄평)를 포함
3. child_age는 도서 연령에 맞게 "2세", "3세", "4세", "5세", "6세", "7세", "8세" 등에서 적절히 배분
4. 리뷰별로 서로 다른 관점과 표현을 사용 (중복 금지)
5. 광고/협찬 느낌 절대 금지. 진짜 읽어본 부모의 솔직한 반응만 작성

## 선택 가능한 뱃지 10종 (이 목록에서만 선택)
{json.dumps(BADGE_LIST, ensure_ascii=False)}

## 출력 형식 (JSON 배열만 반환, 다른 텍스트 금지)
```json
[
  {{
    "rating": 4.5,
    "child_age": "3세",
    "selected_badges": ["🎨 그림체가 좋아요", "⭐ 매일 밤 가져오는 최애 책이에요"],
    "content": "잠자리에서 매일 읽어달라고 해요. 그림이 너무 따뜻해서 저도 좋아하는 책이에요 ☺️"
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
        
        return reviews
    except Exception as e:
        logger.error(f"[{title}] Gemini API 호출 실패: {e}")
        return None


def insert_reviews(book_id: int, book_title: str, reviews: List[dict]):
    """생성된 리뷰를 DB에 삽입"""
    used_nicknames = set()
    
    for review in reviews:
        # 닉네임 중복 방지
        nickname = random.choice([n for n in NICKNAME_POOL if n not in used_nicknames] or NICKNAME_POOL)
        used_nicknames.add(nickname)
        
        # 뱃지 유효성 검증
        selected_badges = [b for b in review.get("selected_badges", []) if b in BADGE_LIST]
        
        data = {
            "book_id": book_id,
            "nickname": nickname,
            "child_age": review.get("child_age"),
            "rating": min(5.0, max(1.0, float(review.get("rating", 4.5)))),
            "selected_badges": selected_badges,
            "content": review.get("content", "")[:500],
            "is_ai_generated": True,
        }
        
        try:
            supabase.table("book_reviews").insert(data).execute()
        except Exception as e:
            logger.error(f"[{book_title}] 리뷰 삽입 실패: {e}")


def main():
    """전체 도서에 대해 AI 시드 리뷰 생성 및 적재"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI 시드 리뷰 자동 생성")
    parser.add_argument("--limit", type=int, default=0, help="처리할 도서 수 제한 (0=전체)")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="이미 리뷰가 있는 도서 건너뛰기")
    parser.add_argument("--dry-run", action="store_true", help="DB 삽입 없이 생성만 테스트")
    args = parser.parse_args()
    
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # 전체 도서 목록 조회
    logger.info("도서 목록 조회 중...")
    result = supabase.table("childbook_items").select("id, title, author, age, category, curation_tag").execute()
    books = result.data or []
    logger.info(f"총 {len(books)}권의 도서 확인")
    
    # 이미 리뷰가 있는 도서 ID 조회
    existing_book_ids = set()
    if args.skip_existing:
        existing_result = supabase.table("book_reviews").select("book_id").execute()
        existing_book_ids = {r["book_id"] for r in (existing_result.data or [])}
        logger.info(f"이미 리뷰가 있는 도서: {len(existing_book_ids)}권 (건너뜀)")
    
    # 처리 대상 필터링
    target_books = [b for b in books if b["id"] not in existing_book_ids]
    if args.limit > 0:
        target_books = target_books[:args.limit]
    
    logger.info(f"처리 대상: {len(target_books)}권")
    
    success_count = 0
    fail_count = 0
    
    for i, book in enumerate(target_books, 1):
        book_id = book["id"]
        title = book.get("title", f"ID:{book_id}")
        logger.info(f"[{i}/{len(target_books)}] {title} 리뷰 생성 중...")
        
        reviews = generate_reviews_for_book(book)
        
        if not reviews:
            fail_count += 1
            continue
        
        if args.dry_run:
            logger.info(f"  [DRY RUN] 생성된 리뷰 {len(reviews)}개:")
            for r in reviews:
                logger.info(f"    ⭐{r.get('rating')} | {r.get('content', '')[:50]}...")
        else:
            insert_reviews(book_id, title, reviews)
            logger.info(f"  ✅ {len(reviews)}개 리뷰 적재 완료")
        
        success_count += 1
        
        # API Rate Limit 방지
        time.sleep(1.5)
    
    logger.info(f"\n===== 완료 =====")
    logger.info(f"성공: {success_count}권 | 실패: {fail_count}권")


if __name__ == "__main__":
    main()
