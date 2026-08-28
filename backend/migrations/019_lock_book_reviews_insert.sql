-- ============================================
-- 019_lock_book_reviews_insert.sql
-- 목적: book_reviews에 대한 anon(공개) INSERT 허용 정책 제거
--   - 기존 "book_reviews_insert_all" 정책(WITH CHECK (true))은
--     NEXT_PUBLIC_SUPABASE_ANON_KEY만 있으면 누구나 백엔드를 거치지 않고
--     Supabase에 직접 리뷰를 삽입할 수 있게 해, 백엔드의 뱃지 화이트리스트/
--     글자수 제한/닉네임 규칙을 전부 우회할 수 있었습니다.
--   - 리뷰 작성은 반드시 POST /api/books/{book_id}/reviews (서비스 롤 키 사용)를
--     거치도록 강제합니다. 서비스 롤 키는 RLS를 우회하므로 백엔드 동작에는
--     영향이 없습니다.
-- ============================================

DROP POLICY IF EXISTS "book_reviews_insert_all" ON book_reviews;

CREATE POLICY "book_reviews_insert_service_only" ON book_reviews
    FOR INSERT WITH CHECK (false);

-- 조회는 기존과 동일하게 모든 사용자(비로그인 포함) 허용 유지
-- ("book_reviews_select_all" 정책은 그대로 둡니다)
