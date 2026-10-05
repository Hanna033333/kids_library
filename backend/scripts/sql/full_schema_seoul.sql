-- ==============================================================================
-- 책자리 (Kids Library) - Seoul (ap-northeast-2) 전체 스키마 초기화 SQL
-- ==============================================================================

-- 1. UUID 확장 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. childbook_items (도서 메인 테이블)
CREATE TABLE IF NOT EXISTS public.childbook_items (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    publisher TEXT,
    isbn TEXT UNIQUE,
    pangyo_callno TEXT,
    similarity NUMERIC,
    owned BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    page TEXT,
    age TEXT,
    category TEXT,
    price TEXT,
    keywords TEXT,
    image_url TEXT,
    vol TEXT,
    description TEXT,
    curation_tag TEXT,
    is_hidden BOOLEAN DEFAULT false,
    web_scraped_callno TEXT,
    curation_note TEXT,
    confidence_score NUMERIC,
    national_loan_count INTEGER DEFAULT 0,
    page_count INTEGER,
    text_level TEXT,
    preview_urls JSONB,
    library_callnos JSONB DEFAULT '{}'::jsonb
);

-- 3. book_library_info (도서관별 소장/청구기호 테이블)
CREATE TABLE IF NOT EXISTS public.book_library_info (
    id BIGSERIAL PRIMARY KEY,
    book_id BIGINT NOT NULL REFERENCES public.childbook_items(id) ON DELETE CASCADE,
    library_name TEXT NOT NULL,
    callno TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. book_reviews (부모 도서 한줄평 및 공감 뱃지 테이블)
CREATE TABLE IF NOT EXISTS public.book_reviews (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    book_id BIGINT NOT NULL REFERENCES public.childbook_items(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    rating NUMERIC(2,1) CHECK (rating >= 1.0 AND rating <= 5.0),
    comment TEXT,
    nickname TEXT NOT NULL,
    child_age TEXT,
    selected_badges TEXT[] DEFAULT '{}',
    content TEXT,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. threads_feeds (스레드 자동 발행 피드 테이블)
CREATE TABLE IF NOT EXISTS public.threads_feeds (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    image_urls TEXT[],
    book_ids BIGINT[],
    curation_tag TEXT,
    scheduled_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    is_approved BOOLEAN DEFAULT FALSE,
    card_descriptions JSONB,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. members (회원 프로필 테이블)
CREATE TABLE IF NOT EXISTS public.members (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    nickname TEXT,
    profile_image_url TEXT,
    preferred_library TEXT,
    provider TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    agreed_to_terms BOOLEAN NOT NULL DEFAULT false,
    agreed_to_privacy BOOLEAN NOT NULL DEFAULT false,
    agreed_to_marketing BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider, provider_id)
);

-- 7. wishlists (찜하기/북마크 테이블)
CREATE TABLE IF NOT EXISTS public.wishlists (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.members(id) ON DELETE CASCADE,
    book_id BIGINT NOT NULL REFERENCES public.childbook_items(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, book_id)
);

-- 8. callno_history (청구기호 변경 이력 테이블)
CREATE TABLE IF NOT EXISTS public.callno_history (
    id BIGSERIAL PRIMARY KEY,
    book_id BIGINT NOT NULL REFERENCES public.childbook_items(id) ON DELETE CASCADE,
    old_callno TEXT,
    new_callno TEXT,
    change_type TEXT NOT NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

-- ==============================================================================
-- 인덱스 생성
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_childbook_isbn ON public.childbook_items(isbn);
CREATE INDEX IF NOT EXISTS idx_childbook_pangyo_callno ON public.childbook_items(pangyo_callno) WHERE pangyo_callno IS NOT NULL AND pangyo_callno != '없음';
CREATE INDEX IF NOT EXISTS idx_childbook_title ON public.childbook_items(title);
CREATE INDEX IF NOT EXISTS idx_childbook_title_lower ON public.childbook_items(LOWER(title));
CREATE INDEX IF NOT EXISTS idx_childbook_author_lower ON public.childbook_items(LOWER(author));
CREATE INDEX IF NOT EXISTS idx_childbook_age ON public.childbook_items(age);
CREATE INDEX IF NOT EXISTS idx_childbook_pangyo_title ON public.childbook_items(pangyo_callno, title) WHERE pangyo_callno IS NOT NULL AND pangyo_callno != '없음';

CREATE INDEX IF NOT EXISTS idx_book_library_info_book_id ON public.book_library_info(book_id);
CREATE INDEX IF NOT EXISTS idx_book_library_info_library_name ON public.book_library_info(library_name);

CREATE INDEX IF NOT EXISTS idx_book_reviews_book_id ON public.book_reviews(book_id);
CREATE INDEX IF NOT EXISTS idx_book_reviews_created_at ON public.book_reviews(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_members_email ON public.members(email);
CREATE INDEX IF NOT EXISTS idx_members_provider ON public.members(provider, provider_id);
CREATE INDEX IF NOT EXISTS idx_wishlists_user_id ON public.wishlists(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlists_book_id ON public.wishlists(book_id);

CREATE INDEX IF NOT EXISTS idx_callno_history_book_id ON public.callno_history(book_id);

-- ==============================================================================
-- RLS (Row Level Security) 설정
-- ==============================================================================

-- childbook_items RLS
ALTER TABLE public.childbook_items ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read access for childbook_items" ON public.childbook_items;
CREATE POLICY "Public read access for childbook_items" ON public.childbook_items FOR SELECT USING (true);
CREATE POLICY "Service role full access for childbook_items" ON public.childbook_items TO service_role USING (true) WITH CHECK (true);

-- book_library_info RLS
ALTER TABLE public.book_library_info ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Public read access" ON public.book_library_info;
CREATE POLICY "Public read access" ON public.book_library_info FOR SELECT USING (true);
CREATE POLICY "Service role full access for book_library_info" ON public.book_library_info TO service_role USING (true) WITH CHECK (true);

-- book_reviews RLS
ALTER TABLE public.book_reviews ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "book_reviews_select_all" ON public.book_reviews;
DROP POLICY IF EXISTS "book_reviews_insert_all" ON public.book_reviews;
DROP POLICY IF EXISTS "book_reviews_insert_authenticated" ON public.book_reviews;
DROP POLICY IF EXISTS "book_reviews_insert_service_only" ON public.book_reviews;
CREATE POLICY "book_reviews_select_all" ON public.book_reviews FOR SELECT USING (true);
CREATE POLICY "book_reviews_insert_service_only" ON public.book_reviews FOR INSERT WITH CHECK (false);
CREATE POLICY "Service role full access for book_reviews" ON public.book_reviews TO service_role USING (true) WITH CHECK (true);

-- threads_feeds RLS
ALTER TABLE public.threads_feeds ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow service role fully" ON public.threads_feeds;
CREATE POLICY "Allow service role fully" ON public.threads_feeds TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Public read access for threads_feeds" ON public.threads_feeds FOR SELECT USING (true);

-- callno_history RLS
ALTER TABLE public.callno_history ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Service role full access for callno_history" ON public.callno_history;
CREATE POLICY "Service role full access for callno_history" ON public.callno_history TO service_role USING (true) WITH CHECK (true);

-- members RLS
ALTER TABLE public.members ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own data" ON public.members FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own data" ON public.members FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own data" ON public.members FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Service role full access for members" ON public.members TO service_role USING (true) WITH CHECK (true);

-- wishlists RLS
ALTER TABLE public.wishlists ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own wishlists" ON public.wishlists FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own wishlists" ON public.wishlists FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own wishlists" ON public.wishlists FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Service role full access for wishlists" ON public.wishlists TO service_role USING (true) WITH CHECK (true);

-- ==============================================================================
-- 닉네임 자동 생성 & 신규 가입자 트리거 함수
-- ==============================================================================

CREATE OR REPLACE FUNCTION public.generate_random_nickname()
RETURNS TEXT AS $$
DECLARE
  adjectives TEXT[] := ARRAY[
    '지혜로운', '따스한', '포근한', '정겨운', '행복한', '다정한', '꿈꾸는', '다독이는', '슬기로운', '다복한', 
    '마음넓은', '빛나는', '즐거운', '상냥한', '반짝이는', '용감한', '푸른', '희망찬', '해맑은', '고마운', 
    '포근포근', '싱그러운', '너그러운', '새싹같은', '옹달샘', '보드라운', '초롱초롱', '알록달록', '은은한', '산뜻한',
    '사랑스런', '명랑한', '슬기찬', '어질고', '호기심찬', '눈부신', '도란도란', '달콤한', '미소짓는', '소담한',
    '재치있는', '기운찬', '활기찬', '따사로운', '아늑한', '별처럼', '구름같은', '무지개빛', '정다운', '온화한',
    '단단한', '자유로운', '맑고밝은', '조잘조잘', '살가운', '도란대는', '생글생글', '두근두근', '소복소복', '풍성한',
    '향기로운', '든든한', '기쁨가득', '마음고운', '생각깊은', '지혜가득', '꿈이많은', '찬란한', '싱글벙글', '방긋웃는',
    '풋풋한', '순수한', '맑은눈의', '꿈꾸듯', '솔솔부는', '똘똘한', '야무진', '의젓한', '씩씩한', '반듯한'
  ];
  nouns TEXT[] := ARRAY[
    '책벌레', '이야기꾼', '책부엉이', '파랑새', '독서가', '책요정', '글벗', '책탐험가', '책마을님', '도토리',
    '꿈나무', '독서왕', '별나무', '책친구', '아기도깨비', '책다람쥐', '토끼', '작은새', '어린사자', '꼬마곰',
    '책박사', '길잡이', '책마법사', '글마루', '책지기', '동화작가', '숲속요정', '별똥별', '새싹', '햇살이',
    '달팽이', '꽃사슴', '아기호랑이', '책누리', '글꽃', '책별', '은하수', '숲속친구', '이야기샘', '책방주인',
    '글타래', '책등대', '지혜샘', '달맞이', '별지기', '숲지기', '꿈꾸미', '도서관지기', '글동무', '책풍경',
    '호기심대장', '상상왕', '생각나무', '독서대장', '마음상자', '이야기별', '책바다', '단풍잎', '은행잎', '솔방울',
    '아기참새', '책정원', '글나라', '동화나무', '책소리', '글소리', '달빛요정', '별빛마을', '작은여우', '아기달님',
    '숲속곰돌이', '꼬마별', '책마중', '글나래', '꿈나래', '새싹지기', '솔바람', '들꽃', '책보따리', '이야기꽃'
  ];
  adj_len INT := array_length(adjectives, 1);
  noun_len INT := array_length(nouns, 1);
  rand_num INT := floor(100 + random() * 900)::int;
BEGIN
  RETURN adjectives[1 + floor(random() * adj_len)::int] || nouns[1 + floor(random() * noun_len)::int] || rand_num::text;
END;
$$ LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
  generated_nick TEXT;
BEGIN
  generated_nick := public.generate_random_nickname();

  INSERT INTO public.members (
    id,
    email,
    provider,
    provider_id,
    nickname,
    agreed_to_terms,
    agreed_to_privacy,
    agreed_to_marketing
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_app_meta_data->>'provider', 'email'),
    COALESCE(NEW.raw_user_meta_data->>'provider_id', NEW.id::text),
    generated_nick,
    true,
    true,
    false
  )
  ON CONFLICT (id) DO UPDATE
  SET nickname = COALESCE(public.members.nickname, EXCLUDED.nickname);

  RETURN NEW;
EXCEPTION
  WHEN OTHERS THEN
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_members_updated_at ON public.members;
CREATE TRIGGER update_members_updated_at
  BEFORE UPDATE ON public.members
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();
