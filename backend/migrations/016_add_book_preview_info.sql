-- 016_add_book_preview_info.sql
-- childbook_items 테이블에 알라딘 연동 페이지 수, 글밥 수준, 내지 미리보기 이미지 URL 컬럼 추가

ALTER TABLE childbook_items 
ADD COLUMN IF NOT EXISTS page_count INTEGER DEFAULT NULL,
ADD COLUMN IF NOT EXISTS text_level TEXT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS preview_urls TEXT[] DEFAULT NULL;

-- 저자별 검색 속도 최적화를 위한 텍스트 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_childbook_items_author ON childbook_items (author);
