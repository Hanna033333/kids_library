-- ============================================
-- 020_add_book_library_info_rls.sql
-- 목적: book_library_info 테이블의 RLS 설정 누락 보완
--   - 프론트엔드(frontend/lib/supabase-client.ts)가 브라우저에서 anon 키로
--     book_library_info를 childbook_items와 조인해 직접 조회하고 있는데,
--     이 테이블은 리포지토리의 어떤 migrations/*.sql, scripts/sql/*.sql 에도
--     RLS 설정이 없었습니다 (Supabase 대시보드에서 수동 생성된 테이블).
--   - 도서관 청구기호 정보는 childbook_items와 마찬가지로 공개 열람용 데이터이므로
--     조회는 허용하고, 쓰기는 서비스 롤 키(백엔드)만 가능하도록 잠급니다.
-- ============================================

ALTER TABLE public.book_library_info ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public read access" ON public.book_library_info;
DROP POLICY IF EXISTS "No public insert" ON public.book_library_info;
DROP POLICY IF EXISTS "No public update" ON public.book_library_info;
DROP POLICY IF EXISTS "No public delete" ON public.book_library_info;

CREATE POLICY "Public read access"
  ON public.book_library_info
  FOR SELECT
  USING (true);

CREATE POLICY "No public insert"
  ON public.book_library_info
  FOR INSERT
  WITH CHECK (false);

CREATE POLICY "No public update"
  ON public.book_library_info
  FOR UPDATE
  USING (false);

CREATE POLICY "No public delete"
  ON public.book_library_info
  FOR DELETE
  USING (false);
