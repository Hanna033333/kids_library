-- ============================================
-- 회원 선호 아이 연령대(preferred_child_age) 컬럼 추가
-- 파일명: 027_add_preferred_child_age.sql
-- ============================================

ALTER TABLE public.members
  ADD COLUMN IF NOT EXISTS preferred_child_age TEXT
  CHECK (preferred_child_age IS NULL OR preferred_child_age IN ('0-3', '4-7', '8-12', '13+'));

COMMENT ON COLUMN public.members.preferred_child_age IS '사용자 설정 우리 아이 선호 연령대 (0-3, 4-7, 8-12, 13+)';

