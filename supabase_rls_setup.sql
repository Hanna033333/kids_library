-- ============================================================
-- 책자리 Supabase 종합 보안 설정 (RLS + 정책)
-- 버전: v2 (2026-04-08) - 전체 테이블 대상 보안 강화
-- ============================================================
-- 📌 실행 방법:
--   1. Supabase Dashboard → SQL Editor
--   2. 이 파일 내용 전체 복사 후 붙여넣기
--   3. Run 버튼 클릭
-- ✅ 성공 기준: 아래 모든 쿼리가 에러 없이 실행됨
-- ============================================================


-- ============================================================
-- 1. childbook_items (도서 데이터)
--    - 모든 사용자(익명 포함): 읽기(SELECT)만 허용
--    - 쓰기/수정/삭제: 완전 차단 (관리자는 Supabase Dashboard 또는 Service Role Key 사용)
-- ============================================================

ALTER TABLE public.childbook_items ENABLE ROW LEVEL SECURITY;

-- 기존 정책 삭제 후 재생성 (중복 방지)
DROP POLICY IF EXISTS "Public read access" ON public.childbook_items;
DROP POLICY IF EXISTS "No public insert" ON public.childbook_items;
DROP POLICY IF EXISTS "No public update" ON public.childbook_items;
DROP POLICY IF EXISTS "No public delete" ON public.childbook_items;

-- 읽기: 누구나 가능 (도서 검색/조회 기능)
CREATE POLICY "Public read access"
  ON public.childbook_items
  FOR SELECT
  USING (true);

-- 쓰기 차단: 익명/일반 유저는 INSERT 불가
CREATE POLICY "No public insert"
  ON public.childbook_items
  FOR INSERT
  WITH CHECK (false);

-- 수정 차단: 익명/일반 유저는 UPDATE 불가
CREATE POLICY "No public update"
  ON public.childbook_items
  FOR UPDATE
  USING (false);

-- 삭제 차단: 익명/일반 유저는 DELETE 불가
CREATE POLICY "No public delete"
  ON public.childbook_items
  FOR DELETE
  USING (false);


-- ============================================================
-- 2. members (회원 정보)
--    - 본인 데이터만 조회/수정 허용
--    - 타인의 회원 정보는 접근 불가
-- ============================================================

ALTER TABLE public.members ENABLE ROW LEVEL SECURITY;

-- 기존 정책 삭제 후 재생성 (중복 방지)
DROP POLICY IF EXISTS "Users can view own data" ON public.members;
DROP POLICY IF EXISTS "Users can update own data" ON public.members;
DROP POLICY IF EXISTS "Users can insert own data" ON public.members;
DROP POLICY IF EXISTS "Users can delete own data" ON public.members;

-- 조회: 본인만 가능
CREATE POLICY "Users can view own data"
  ON public.members
  FOR SELECT
  USING (auth.uid() = id);

-- 수정: 본인만 가능
CREATE POLICY "Users can update own data"
  ON public.members
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- 최초 등록: 본인 ID로만 가능 (트리거 통해 자동 생성; Service Role 권한 필요)
CREATE POLICY "Users can insert own data"
  ON public.members
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- 삭제: 본인만 가능 (회원 탈퇴 시)
CREATE POLICY "Users can delete own data"
  ON public.members
  FOR DELETE
  USING (auth.uid() = id);


-- ============================================================
-- 3. wishlists (찜 목록)
--    - 본인 찜 목록만 조회/추가/삭제 허용
--    - 타인의 찜 목록은 접근 불가
-- ============================================================

ALTER TABLE public.wishlists ENABLE ROW LEVEL SECURITY;

-- 기존 정책 삭제 후 재생성 (중복 방지)
DROP POLICY IF EXISTS "Users can view own wishlists" ON public.wishlists;
DROP POLICY IF EXISTS "Users can insert own wishlists" ON public.wishlists;
DROP POLICY IF EXISTS "Users can delete own wishlists" ON public.wishlists;

-- 조회: 본인 찜 목록만
CREATE POLICY "Users can view own wishlists"
  ON public.wishlists
  FOR SELECT
  USING (auth.uid() = user_id);

-- 추가: 본인 이름으로만 찜 가능
CREATE POLICY "Users can insert own wishlists"
  ON public.wishlists
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- 삭제: 본인 찜만 삭제 가능
CREATE POLICY "Users can delete own wishlists"
  ON public.wishlists
  FOR DELETE
  USING (auth.uid() = user_id);


-- ============================================================
-- 4. callno_history (청구기호 변경 이력)
--    - 운영 내부 데이터: 일반 유저 접근 완전 차단
--    - 관리자는 Supabase Dashboard 또는 Service Role Key 사용
-- ============================================================

ALTER TABLE public.callno_history ENABLE ROW LEVEL SECURITY;

-- 기존 정책 삭제 후 재생성 (중복 방지)
DROP POLICY IF EXISTS "No public access to callno_history" ON public.callno_history;

-- 모든 일반 유저 접근 차단 (SELECT 포함)
CREATE POLICY "No public access to callno_history"
  ON public.callno_history
  FOR ALL
  USING (false);


-- ============================================================
-- ✅ 적용 완료 확인 쿼리 (실행 후 결과 확인용)
-- ============================================================
-- 아래 쿼리를 실행하면 RLS가 활성화된 테이블 목록을 확인할 수 있습니다.
SELECT
  schemaname,
  tablename,
  rowsecurity AS rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('childbook_items', 'members', 'wishlists', 'callno_history')
ORDER BY tablename;
