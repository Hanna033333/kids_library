-- ============================================
-- 회원 시스템 마이그레이션
-- 파일명: 010_create_members_and_wishlists.sql
-- ============================================

-- 1. members 테이블 생성
CREATE TABLE IF NOT EXISTS public.members (
  -- Primary Key (Supabase Auth UID와 동일)
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- 기본 정보
  email TEXT NOT NULL,
  nickname TEXT,
  profile_image_url TEXT,
  
  -- 소셜 로그인 메타데이터
  provider TEXT NOT NULL, -- 'kakao', 'google', 'apple'
  provider_id TEXT NOT NULL,
  
  -- 약관 동의
  agreed_to_terms BOOLEAN NOT NULL DEFAULT false,
  agreed_to_privacy BOOLEAN NOT NULL DEFAULT false,
  agreed_to_marketing BOOLEAN DEFAULT false,
  
  -- 타임스탬프
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- 유니크 제약
  UNIQUE(provider, provider_id)
);

-- 2. wishlists 테이블 생성
CREATE TABLE IF NOT EXISTS public.wishlists (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES public.members(id) ON DELETE CASCADE,
  book_id INTEGER NOT NULL REFERENCES public.childbook_items(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- 중복 방지
  UNIQUE(user_id, book_id)
);

-- 3. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_members_email ON public.members(email);
CREATE INDEX IF NOT EXISTS idx_members_provider ON public.members(provider, provider_id);
CREATE INDEX IF NOT EXISTS idx_wishlists_user_id ON public.wishlists(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlists_book_id ON public.wishlists(book_id);

-- 4. RLS 활성화
ALTER TABLE public.members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wishlists ENABLE ROW LEVEL SECURITY;

-- 5. members 테이블 RLS 정책
CREATE POLICY "Users can view own data"
  ON public.members
  FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own data"
  ON public.members
  FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Users can insert own data"
  ON public.members
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- 6. wishlists 테이블 RLS 정책
CREATE POLICY "Users can view own wishlists"
  ON public.wishlists
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own wishlists"
  ON public.wishlists
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own wishlists"
  ON public.wishlists
  FOR DELETE
  USING (auth.uid() = user_id);

-- 7. 트리거 함수: 회원 가입 시 members 테이블 자동 생성
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.members (id, email, provider, provider_id)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_app_meta_data->>'provider', 'email'),
    COALESCE(NEW.raw_user_meta_data->>'provider_id', NEW.id::text)
  );
  RETURN NEW;
EXCEPTION
  WHEN OTHERS THEN
    -- 에러 발생 시에도 사용자 생성은 계속 진행
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. 트리거 등록
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- 9. 트리거 함수: updated_at 자동 갱신
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 10. updated_at 트리거 등록
DROP TRIGGER IF EXISTS update_members_updated_at ON public.members;
CREATE TRIGGER update_members_updated_at
  BEFORE UPDATE ON public.members
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();
