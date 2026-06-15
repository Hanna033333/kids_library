-- 1. curation_tag 컬럼 추가
ALTER TABLE public.threads_feeds ADD COLUMN IF NOT EXISTS curation_tag VARCHAR(100);

-- 2. scheduled_at 컬럼 추가 (홈페이지 노출 예정일, 기본값은 현재 시각)
ALTER TABLE public.threads_feeds ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL;

-- 3. 기존 정책이 있으면 삭제 후 재생성 (익명 사용자 SELECT용)
DROP POLICY IF EXISTS "Allow public select" ON public.threads_feeds;
CREATE POLICY "Allow public select" ON public.threads_feeds
    FOR SELECT
    USING (true);
