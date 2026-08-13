-- 015: 부모 평점 & 공감 뱃지 소셜 프루프 시스템 테이블 생성
-- 도서 상세 페이지 이탈 방지를 위한 부모 한줄평 + 범용 10종 뱃지 평점 체계

-- 1. book_reviews 테이블 생성
CREATE TABLE IF NOT EXISTS book_reviews (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    book_id BIGINT NOT NULL REFERENCES childbook_items(id) ON DELETE CASCADE,
    nickname TEXT NOT NULL,
    child_age TEXT,                          -- 예: "3세", "5세"
    rating NUMERIC(2,1) CHECK (rating >= 1.0 AND rating <= 5.0),
    selected_badges TEXT[] DEFAULT '{}',     -- 선택한 범용 뱃지 목록
    content TEXT,                            -- 한줄평 본문
    is_ai_generated BOOLEAN DEFAULT FALSE,   -- AI 시드 데이터 구분용 (관리 목적)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 인덱스 생성 (book_id 기준 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_book_reviews_book_id ON book_reviews(book_id);
CREATE INDEX IF NOT EXISTS idx_book_reviews_created_at ON book_reviews(created_at DESC);

-- 3. RLS 활성화 및 정책 설정
ALTER TABLE book_reviews ENABLE ROW LEVEL SECURITY;

-- 기존 정책 제거 (멱등성 보장 — 재실행 시 충돌 방지)
DROP POLICY IF EXISTS "book_reviews_select_all" ON book_reviews;
DROP POLICY IF EXISTS "book_reviews_insert_all" ON book_reviews;

-- 모든 사용자(비로그인 포함) 조회 허용
CREATE POLICY "book_reviews_select_all" ON book_reviews
    FOR SELECT USING (true);

-- 모든 사용자(비로그인 포함) 리뷰 작성 허용
CREATE POLICY "book_reviews_insert_all" ON book_reviews
    FOR INSERT WITH CHECK (true);
