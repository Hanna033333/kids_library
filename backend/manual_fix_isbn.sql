-- 특정 ID의 ISBN을 수동으로 변경하는 쿼리
-- 사용 방법: 변경하려는 대상의 ID와 새로운 ISBN을 입력하여 실행하세요.

-- 예시: ID가 1234인 책의 ISBN을 '9791199999999'로 변경
-- UPDATE childbook_items SET isbn = '9791199999999' WHERE id = 1234;

BEGIN; 

-- 1. 변경할 데이터 확인 (실수 방지)
SELECT id, title, isbn, publisher, created_at 
FROM childbook_items 
WHERE id = 0000; -- 여기에 대상 ID 입력

-- 2. 업데이트 실행
UPDATE childbook_items
SET isbn = '변경할_ISBN' -- 여기에 새 ISBN 입력
WHERE id = 0000; -- 여기에 대상 ID 입력

-- 3. 결과 확인
SELECT id, title, isbn, publisher, updated_at 
FROM childbook_items 
WHERE id = 0000; -- 여기에 대상 ID 입력

COMMIT;
