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
    age = book.get("age", "") or "전연령"
    category = book.get("category", "")
    curation_tag = book.get("curation_tag", "")
    description = (book.get("description") or "정보 없음")[:400]

    # 연령대별 작성 지침 및 child_age 범위 정의
    if any(k in age for k in ["0-3", "0~3", "영아", "0세", "1세", "2세", "3세"]):
        age_guide = """- 이 책은 **0~3세 영아 추천 도서**입니다.
- **child_age 범위**: "1세", "2세", "3세" 중 선택.
- **후기 소재**: 촉감/사운드/보드북 반응, 첫 인지/생활습관(배변, 이닦기, 수면), 부모와의 교감, 오감 자극 등."""
    elif any(k in age for k in ["8-12", "8~12", "초등", "8세", "9세", "10세", "11세", "12세"]):
        age_guide = """- 이 책은 **8~12세 초등학생 추천 도서**입니다.
- **child_age 범위**: "8세", "9세", "10세", "11세", "12세" 중 선택. (상황에 따라 "초등1", "초등3" 등)
- **후기 소재**: 초등 학교생활, 글밥과 독해력, 친구 관계/학교 고민, 교과 연계, 생각의 깊이 확장, 독서록 작성, 자아 성찰 등.
- 🚨 **[절대 금지]**: 어린이집 등원, 아기 보드북, 배변 훈련, 아기 젖병 등 0~4세 영아 관련 소재를 절대로 포함하지 마세요!"""
    else:
        age_guide = """- 이 책은 **4~7세 유아 추천 도서**입니다.
- **child_age 범위**: "4세", "5세", "6세", "7세" 중 선택.
- **후기 소재**: 유치원/어린이집 적응, 사회성, 상상력, 호기심, 옛이야기 감상, 아이와의 대화거리 등."""

    prompt = f"""당신은 3040 한국 부모님들이 앱이나 카카오 채널에 남기는 진짜 도서 후기를 그대로 재현하는 전문가입니다.
다음 어린이 도서의 주제/줄거리 맥락과 추천 연령에 정확히 연관하여, 실제 부모들의 자연스러운 후기 {count}개를 JSON 배열로 생성해주세요.

## 도서 정보
- 제목: {title}
- 저자: {author}
- 추천 연령: {age}
- 카테고리: {category}
- 큐레이션 태그: {curation_tag}
- 책 줄거리/소재 참고: {description}

## 연령대별 필수 지침 (반드시 준수)
{age_guide}

## 핵심 작성 규칙 (반드시 엄수)
1. **도서 추천 연령 및 줄거리/소재에 100% 매칭 (최우선)**:
   - 8~12세 초등 도서에 영아용(등원, 배변 훈련, 젖병 등) 이야기를 쓰지 마세요.
   - 책의 실제 소재(예: 고아원, 가족사랑, 우주, 전래동화, 공룡 등)와 연관된 부모의 계기와 아이의 실제 반응을 적어주세요.
2. **줄거리 직접 요약 금지**:
   - ❌ "이 책은 주인공 누구와 누구의 스토리입니다" 식의 줄거리 요약 금지.
   - ⭕ 부모로서 이 책을 읽혀주었을 때 아이의 반응과 대화, 변화된 부분에 집중하세요.
3. **길이와 문체를 다양하게 섞기 (가장 중요)**:
   - {count}개 중 **1~2개는 짧고 솔직한 한 줄 후기** (15~30자)로 작성하세요.
     → 예시: "좋아요 아이가 너무 좋아해요", "강추요~ 다음편도 구매할게요", "그냥 좋아요", "아이가 매일 꺼내봐요", "완전 좋아요ㅎㅎ", "사길 잘했어요"
   - 나머지는 **1~2문장의 자연스러운 구어체** (40~70자)로 작성하되, 완벽하게 다듬어진 문장보다는 실제 타이핑한 것처럼 약간 자연스러운 느낌으로 써주세요.
   - **AI가 쓴 것처럼 정돈된 문장 패턴 (예: "~하는 책입니다. 아이와 함께 읽어보세요.") 절대 금지.**
4. 각 리뷰마다 rating(4.0~5.0 사이 소수점 1자리), child_age(위 연령 지침에 따름), selected_badges(아래 10종 중 1~3개 선택), content(후기 본문)를 포함하세요.

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
        content_text = review.get("content", "")[:500]
        data_new = {
            "book_id": book_id,
            "nickname": nickname,
            "child_age": review.get("child_age"),
            "rating": int(round(min(5.0, max(1.0, float(review.get("rating", 4.5)))))),
            "selected_badges": selected_badges,
            "content": content_text,
            "comment": content_text,  # NOT NULL 제약 충족
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
    """홈 화면 큐레이션 및 대표 인기 도서들에 대해 시드 리뷰 생성 및 적재"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI 시드 리뷰 자동 생성")
    parser.add_argument("--limit", type=int, default=100, help="처리할 도서 수 제한 (기본값: 100권)")
    parser.add_argument("--skip-existing", action="store_true", default=False, help="이미 리뷰가 있는 도서 건너뛰기")
    parser.add_argument("--clean-existing", action="store_true", default=False, help="기존 AI 생성 시드 리뷰 전체 삭제 후 재생성")
    parser.add_argument("--dry-run", action="store_true", help="DB 삽입 없이 생성만 테스트")
    args = parser.parse_args()
    
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    if args.clean_existing and not args.dry_run:
        logger.info("🧹 기존 AI 생성 시드 리뷰 전체 삭제 진행 중...")
        try:
            # is_ai_generated = true 인 AI 시드 리뷰만 삭제 (진짜 유저 리뷰 보호)
            del_res = supabase.table("book_reviews").delete().eq("is_ai_generated", True).execute()
            logger.info("✅ AI 생성 시드 리뷰 전체 삭제 완료 (유저 리뷰 보존)")
        except Exception as e:
            logger.error(f"기존 리뷰 삭제 중 오류: {e}")
    
    # 1. 큐레이션 및 인기 도서 목록 균형 추출
    logger.info("큐레이션 및 연령별 대표 도서 목록 추출 중 (Book 8034 필수 포함)...")
    books_map = {}

    # Book 8034 (사용자가 지적한 8-12세 도서 필수 포함)
    b8034_res = supabase.table("childbook_items").select("id, title, author, age, category, curation_tag, national_loan_count, description").eq("id", 8034).execute()
    if b8034_res.data:
        books_map[8034] = b8034_res.data[0]

    # (1) 대표 큐레이션 인기 도서 40권
    res1 = supabase.table("childbook_items").select("id, title, author, age, category, curation_tag, national_loan_count, description")\
        .not_.is_("curation_tag", "null")\
        .order("national_loan_count", desc=True).limit(40).execute()
    for b in (res1.data or []):
        books_map[b["id"]] = b

    # (2) 8~12세 (초등) 인기 도서 20권
    res2 = supabase.table("childbook_items").select("id, title, author, age, category, curation_tag, national_loan_count, description")\
        .eq("age", "8-12").order("national_loan_count", desc=True).limit(20).execute()
    for b in (res2.data or []):
        books_map[b["id"]] = b

    # (3) 0~3세 (영아) 인기 도서 15권
    res3 = supabase.table("childbook_items").select("id, title, author, age, category, curation_tag, national_loan_count, description")\
        .eq("age", "0-3").order("national_loan_count", desc=True).limit(15).execute()
    for b in (res3.data or []):
        books_map[b["id"]] = b

    # (4) 4~7세 (유아) 인기 도서 25권
    res4 = supabase.table("childbook_items").select("id, title, author, age, category, curation_tag, national_loan_count, description")\
        .eq("age", "4-7").order("national_loan_count", desc=True).limit(25).execute()
    for b in (res4.data or []):
        books_map[b["id"]] = b

    books = list(books_map.values())
    if args.limit and len(books) > args.limit:
        books = books[:args.limit]

    logger.info(f"타겟 도서: 총 {len(books)}권 선별 완료 (Book 8034 포함 여부: {8034 in books_map})")
    
    success_count = 0
    fail_count = 0
    total_inserted = 0
    
    for i, book in enumerate(books, 1):
        book_id = book["id"]
        title = book.get("title", f"ID:{book_id}")

        if args.skip_existing and not args.clean_existing:
            check_exist = supabase.table("book_reviews").select("id").eq("book_id", book_id).execute()
            if check_exist.data and len(check_exist.data) > 0:
                logger.info(f"[{i}/{len(books)}] {title} - 이미 리뷰 존재하여 스킵")
                continue
        
        # 상위 도서는 4~5개, 나머지는 2~3개 생성
        if i <= 20:
            target_review_count = random.randint(4, 5)
        else:
            target_review_count = random.randint(2, 3)
            
        logger.info(f"[{i}/{len(books)}] {title} (연령: {book.get('age')}) 리뷰 {target_review_count}개 생성 중...")
        
        reviews = generate_reviews_for_book(book, count=target_review_count)
        
        if not reviews:
            fail_count += 1
            continue
        
        if args.dry_run:
            logger.info(f"  [DRY RUN] 생성된 리뷰 {len(reviews)}개:")
            for r in reviews:
                logger.info(f"    ⭐{r.get('rating')} | [{r.get('child_age')}] {r.get('content', '')[:60]}...")
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
        time.sleep(1.0)
    
    logger.info(f"\n===== 시드 리뷰 적재 작업 완료 =====")
    logger.info(f"성공 도서: {success_count}권 | 실패: {fail_count}권 | 총 생성 및 적재된 리뷰: {total_inserted}개")


if __name__ == "__main__":
    main()
