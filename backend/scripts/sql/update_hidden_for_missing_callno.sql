-- 청구기호가 없는 경우 is_hidden = true로 설정하는 쿼리
-- 대상: pangyo_callno가 NULL이거나, 빈 문자열('')이거나, '없음'인 경우

BEGIN;

UPDATE childbook_items
SET is_hidden = true
WHERE pangyo_callno IS NULL 
   OR pangyo_callno = '' 
   OR pangyo_callno = '없음';

-- 결과 확인 (업데이트된 행의 개수와 내용 대략 확인)
-- SELECT id, title, pangyo_callno, is_hidden FROM childbook_items WHERE is_hidden = true;

COMMIT;
