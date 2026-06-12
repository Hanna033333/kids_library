-- ID 11406 항목을 숨김 처리(is_hidden=true)하는 쿼리

BEGIN;

-- 1. 숨길 항목 확인
SELECT id, title, is_hidden 
FROM childbook_items 
WHERE id = 11406;

-- 2. 업데이트 실행
UPDATE childbook_items
SET is_hidden = true
WHERE id = 11406;

-- 3. 결과 확인
SELECT id, title, is_hidden 
FROM childbook_items 
WHERE id = 11406;

COMMIT;
