-- ============================================
-- 018_remove_auto_member_trigger.sql
-- 목적: 약관 미동의 회원 자동 저장 방지
--   1. auth.users 생성 시 members 테이블에 자동 INSERT하던 트리거 제거
--   2. 기존 약관 미동의(FALSE) 더미 레코드 정리
-- ============================================

-- 1. 트리거 삭제
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- 2. 트리거 함수 삭제
DROP FUNCTION IF EXISTS public.handle_new_user();

-- 3. 약관 미동의 임시 데이터 정리 (agreed_to_terms=false인 레코드 삭제)
-- 주의: 실행 전 반드시 아래 SELECT로 영향 대상을 먼저 확인할 것
-- SELECT * FROM public.members WHERE agreed_to_terms = false;
DELETE FROM public.members
WHERE agreed_to_terms = false AND agreed_to_privacy = false;
