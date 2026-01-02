-- 청구기호 히스토리 테이블 생성
-- Supabase SQL Editor에서 실행

-- 1. 히스토리 테이블 생성
CREATE TABLE IF NOT EXISTS callno_history (
    id BIGSERIAL PRIMARY KEY,
    book_id BIGINT NOT NULL,
    old_callno TEXT,
    new_callno TEXT,
    change_type TEXT NOT NULL, -- 'web_scraping', 'manual_update', 'initial' 등
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    CONSTRAINT fk_book 
        FOREIGN KEY (book_id) 
        REFERENCES childbook_items(id) 
        ON DELETE CASCADE
);

-- 2. 인덱스 생성 (빠른 조회를 위해)
CREATE INDEX IF NOT EXISTS idx_callno_history_book_id ON callno_history(book_id);
CREATE INDEX IF NOT EXISTS idx_callno_history_changed_at ON callno_history(changed_at);

-- 3. 현재 청구기호를 히스토리에 백업 (초기 데이터)
INSERT INTO callno_history (book_id, old_callno, new_callno, change_type, notes)
SELECT 
    id,
    NULL as old_callno,
    pangyo_callno as new_callno,
    'initial' as change_type,
    'Initial call number from database' as notes
FROM childbook_items
WHERE pangyo_callno IS NOT NULL
ON CONFLICT DO NOTHING;

-- 4. 웹 스크래핑으로 변경된 청구기호 기록
INSERT INTO callno_history (book_id, old_callno, new_callno, change_type, notes)
SELECT 
    id,
    pangyo_callno as old_callno,
    web_scraped_callno as new_callno,
    'web_scraping' as change_type,
    'Updated from web scraping (2026-01-02)' as notes
FROM childbook_items
WHERE web_scraped_callno IS NOT NULL
  AND pangyo_callno IS NOT NULL
  AND pangyo_callno != web_scraped_callno
ON CONFLICT DO NOTHING;

-- 5. 조회 예시
-- 특정 책의 청구기호 변경 이력 조회
-- SELECT * FROM callno_history WHERE book_id = 9775 ORDER BY changed_at DESC;

-- 모든 변경 이력 조회 (최근 20건)
-- SELECT 
--     h.*,
--     b.title,
--     b.author
-- FROM callno_history h
-- JOIN childbook_items b ON h.book_id = b.id
-- ORDER BY h.changed_at DESC
-- LIMIT 20;
