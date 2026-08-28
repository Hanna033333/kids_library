-- ============================================
-- 021_add_user_id_to_book_reviews.sql
-- 목적: book_reviews에 user_id 컬럼 추가 및 본인 리뷰 수정/삭제 RLS 정책 설정
--   - user_id: Supabase auth.users의 UUID (로그인 유저와 리뷰 연결)
--   - AI 시드 리뷰는 user_id = NULL 유지 (기존 데이터 영향 없음)
--   - 로그인 유저만 INSERT 가능, 본인 리뷰만 UPDATE/DELETE 가능
-- ============================================

-- 1. user_id 컬럼 추가 (기존 AI 시드 리뷰는 NULL 허용)
ALTER TABLE book_reviews
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;

-- 2. user_id 인덱스 (내 리뷰 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_book_reviews_user_id ON book_reviews(user_id);

-- 3. 기존 정책 정리
DROP POLICY IF EXISTS "book_reviews_update_own" ON book_reviews;
DROP POLICY IF EXISTS "book_reviews_delete_own" ON book_reviews;

-- 4. 본인 리뷰만 수정 허용
CREATE POLICY "book_reviews_update_own" ON book_reviews
    FOR UPDATE USING (
        auth.uid() IS NOT NULL
        AND auth.uid() = user_id
    );

-- 5. 본인 리뷰만 삭제 허용
CREATE POLICY "book_reviews_delete_own" ON book_reviews
    FOR DELETE USING (
        auth.uid() IS NOT NULL
        AND auth.uid() = user_id
    );
