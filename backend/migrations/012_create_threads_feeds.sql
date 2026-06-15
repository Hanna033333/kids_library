CREATE TABLE IF NOT EXISTS public.threads_feeds (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    image_urls TEXT[], -- 카드뉴스 이미지 URL 배열
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    book_ids INTEGER[]
);

-- RLS 활성화
ALTER TABLE public.threads_feeds ENABLE ROW LEVEL SECURITY;

-- 기존 정책이 있으면 삭제 후 재생성
DROP POLICY IF EXISTS "Allow service role fully" ON public.threads_feeds;

-- service_role은 전체 CRUD 권한 부여 (백엔드 제어용)
CREATE POLICY "Allow service role fully" ON public.threads_feeds
    USING (true)
    WITH CHECK (true);
