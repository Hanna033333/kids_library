-- Supabase에서 실행할 SQL
-- 눈의 여왕 숨기기 (is_hidden 컬럼은 이미 존재)

UPDATE childbook_items 
SET is_hidden = TRUE 
WHERE title = '눈의 여왕';
