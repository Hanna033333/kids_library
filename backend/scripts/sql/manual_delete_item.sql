-- 특정 ID의 데이터를 수동으로 삭제하는 쿼리
-- 사용 방법: 삭제하려는 대상의 ID를 입력하여 실행하세요.

BEGIN;

-- 1. 삭제할 데이터 확인 (실수 방지: 제목과 ISBN 확인)
SELECT id, title, isbn, publisher, created_at 
FROM childbook_items 
WHERE id = 0000; -- 여기에 대상 ID 입력

-- 2. 삭제 실행
DELETE FROM childbook_items
WHERE id = 0000; -- 여기에 대상 ID 입력

-- 3. 결과 확인 (삭제되었으므로 조회되지 않아야 함)
SELECT id, title, isbn 
FROM childbook_items 
WHERE id = 0000; -- 여기에 대상 ID 입력

COMMIT;
