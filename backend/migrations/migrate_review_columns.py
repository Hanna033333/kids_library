"""
book_reviews 테이블 마이그레이션 스크립트

기존 스키마:
  id, book_id, user_id, rating, comment, created_at

목표 스키마 (추가 컬럼):
  + nickname       TEXT        -- 작성자 닉네임
  + child_age      TEXT        -- 자녀 연령 (예: "5세")
  + selected_badges TEXT[]     -- 선택된 뱃지 배열
  + content        TEXT        -- 한줄평 본문 (기존 comment에서 분리)
  + is_ai_generated BOOLEAN    -- AI 생성 예시 여부

실행 방법:
  1. Supabase 대시보드 > SQL Editor에서 Step 1 DDL 먼저 실행
  2. 그 후 이 스크립트 실행:
     cd backend && source venv/bin/activate
     python3 migrations/migrate_review_columns.py

기존 comment 포맷 (파싱 대상):
  "닉네임님 [나이] (뱃지1, 뱃지2, ...) 리뷰내용"
  예: "샘깊은이야기꾼님 [11세] (⭐ 우리 아이 최애 책이에요, 💬 아이와 대화거리가 풍부해져요) 아이가..."
"""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.database import supabase
except ImportError:
    print("❌ core.database import 실패. backend 디렉토리에서 실행하세요.")
    sys.exit(1)

# ──────────────────────────────────────────────
# Step 1: Supabase 대시보드에서 먼저 실행할 DDL
# ──────────────────────────────────────────────
SUPABASE_DDL = """
-- book_reviews 테이블에 신규 컬럼 추가 (이미 존재하면 무시)
ALTER TABLE book_reviews
  ADD COLUMN IF NOT EXISTS nickname TEXT,
  ADD COLUMN IF NOT EXISTS child_age TEXT,
  ADD COLUMN IF NOT EXISTS selected_badges TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS content TEXT,
  ADD COLUMN IF NOT EXISTS is_ai_generated BOOLEAN DEFAULT FALSE;

-- 인덱스 (선택)
CREATE INDEX IF NOT EXISTS idx_book_reviews_book_id ON book_reviews(book_id);
CREATE INDEX IF NOT EXISTS idx_book_reviews_user_id ON book_reviews(user_id);
"""

# ──────────────────────────────────────────────
# comment 파서
# ──────────────────────────────────────────────
def parse_comment(comment: str) -> dict:
    """
    "닉네임님 [나이] (뱃지1, 뱃지2) 본문" 형식 파싱.
    매칭 실패 시 nickname=None, child_age=None, selected_badges=[], content=comment 원문.
    """
    if not comment:
        return {"nickname": None, "child_age": None, "selected_badges": [], "content": None}

    result = {
        "nickname": None,
        "child_age": None,
        "selected_badges": [],
        "content": comment.strip(),
    }

    # 닉네임 추출: 앞부분에서 "님" 이전
    nickname_match = re.match(r'^(.+?)님', comment)
    if nickname_match:
        result["nickname"] = nickname_match.group(1).strip()

    # 나이 추출: [나이] 패턴
    age_match = re.search(r'\[(\d+\s*세(?:\s*이상)?)\]', comment)
    if age_match:
        result["child_age"] = age_match.group(1).strip()

    # 뱃지 추출: (...) 괄호 안
    badge_match = re.search(r'\(([^)]+)\)', comment)
    if badge_match:
        raw_badges = badge_match.group(1)
        badges = [b.strip() for b in raw_badges.split(',') if b.strip()]
        result["selected_badges"] = badges

    # 본문 추출: 괄호 이후 텍스트
    if badge_match:
        rest = comment[badge_match.end():].strip()
        result["content"] = rest if rest else None
    elif nickname_match:
        rest = comment[nickname_match.end():].strip()
        rest = re.sub(r'\[\d+\s*세(?:\s*이상)?\]\s*', '', rest).strip()
        result["content"] = rest if rest else None

    return result


# ──────────────────────────────────────────────
# Step 2: 기존 데이터 마이그레이션
# ──────────────────────────────────────────────
def migrate():
    print("=" * 60)
    print("📋 book_reviews 마이그레이션 시작")
    print("=" * 60)
    print()
    print("⚠️  STEP 1: 먼저 Supabase 대시보드 > SQL Editor에서 아래 DDL을 실행하세요:")
    print()
    print(SUPABASE_DDL)
    print()

    input("DDL 실행 완료 후 엔터를 눌러 데이터 마이그레이션을 시작하세요 (Ctrl+C로 취소): ")

    print("\n🔍 기존 리뷰 데이터 조회 중...")
    result = supabase.table("book_reviews").select("id, comment, nickname, selected_badges").execute()
    all_reviews = result.data or []
    print(f"  총 {len(all_reviews)}건 발견")

    to_migrate = [r for r in all_reviews if not r.get("nickname") and r.get("comment")]
    print(f"  마이그레이션 대상: {len(to_migrate)}건 (nickname 없고 comment 있는 것)")

    if not to_migrate:
        print("✅ 모두 이미 마이그레이션되어 있습니다.")
        return

    success = 0
    fail = 0
    skipped = 0

    for review in to_migrate:
        rid = review["id"]
        comment = review.get("comment", "")

        if not comment:
            skipped += 1
            continue

        parsed = parse_comment(comment)

        update_data = {
            "nickname": parsed["nickname"] or "익명 부모님",
            "child_age": parsed["child_age"],
            "selected_badges": parsed["selected_badges"],
            "content": parsed["content"],
            "is_ai_generated": False,
        }

        try:
            supabase.table("book_reviews").update(update_data).eq("id", rid).execute()
            success += 1
            nick = parsed["nickname"] or "익명"
            badges_str = ", ".join(parsed["selected_badges"][:2]) if parsed["selected_badges"] else "(없음)"
            print(f"  ✅ [{rid[:8]}...] {nick} | {parsed['child_age'] or '-'} | 뱃지: {badges_str}")
        except Exception as e:
            fail += 1
            print(f"  ❌ [{rid[:8]}...] 실패: {e}")

    print()
    print("=" * 60)
    print(f"🎉 마이그레이션 완료: 성공 {success}건 / 실패 {fail}건 / 건너뜀 {skipped}건")
    print("=" * 60)


def dry_run():
    """실제 DB 수정 없이 파싱 결과만 미리 확인"""
    print("🔍 DRY RUN: comment 파싱 결과 미리보기")
    result = supabase.table("book_reviews").select("id, comment").limit(10).execute()
    reviews = result.data or []

    for r in reviews:
        comment = r.get("comment", "")
        if not comment:
            continue
        parsed = parse_comment(comment)
        print(f"\n  원본: {comment[:80]}...")
        print(f"  → 닉네임: {parsed['nickname']}")
        print(f"  → 나이: {parsed['child_age']}")
        print(f"  → 뱃지: {parsed['selected_badges']}")
        print(f"  → 본문: {(parsed['content'] or '')[:60]}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        dry_run()
    else:
        migrate()
