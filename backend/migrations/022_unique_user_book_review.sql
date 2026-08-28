-- ============================================
-- 022_unique_user_book_review.sql
-- 목적: 동일 유저가 같은 책에 리뷰를 중복 등록하는 것을 DB 레벨에서 차단
--   - (user_id, book_id) 쌍에 부분 Unique 인덱스 적용
--   - AI 생성 예시 리뷰(user_id = NULL)는 중복 제약 제외
--   - 기존 중복 데이터 존재 시 최신 리뷰 1개만 보존 후 인덱스 생성
-- ============================================

-- 1. 중복 리뷰 제거 (동일 user_id + book_id 중 가장 최근 것만 유지)
DELETE FROM book_reviews
WHERE id NOT IN (
    SELECT DISTINCT ON (user_id, book_id) id
    FROM book_reviews
    WHERE user_id IS NOT NULL
    ORDER BY user_id, book_id, created_at DESC
)
AND user_id IS NOT NULL;

-- 2. 부분 Unique 인덱스 생성 (user_id IS NOT NULL 인 행만 적용)
CREATE UNIQUE INDEX IF NOT EXISTS uix_book_reviews_user_book
    ON book_reviews (user_id, book_id)
    WHERE user_id IS NOT NULL;
