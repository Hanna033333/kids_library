-- 1. childbook_items 테이블에 national_loan_count 컬럼 추가 (기본값 0)
ALTER TABLE public.childbook_items ADD COLUMN IF NOT EXISTS national_loan_count INTEGER DEFAULT 0 NOT NULL;

-- 2. 검색 및 대출순 정렬 성능 최적화를 위한 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_childbook_national_loan ON public.childbook_items(national_loan_count DESC);
