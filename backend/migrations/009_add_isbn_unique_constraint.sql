-- 1. 중복 ISBN 확인 (선택 사항: 실행 전 확인용)
-- SELECT isbn, COUNT(*) FROM childbook_items GROUP BY isbn HAVING COUNT(*) > 1;

-- 2. 중복 제거 (가장 최근에 추가된 항목 유지)
-- 주의: 이 쿼리는 중복된 ISBN 중 id가 가장 큰(최신) 레코드만 남기고 나머지를 삭제합니다.
DELETE FROM childbook_items a 
USING childbook_items b 
WHERE a.id < b.id AND a.isbn = b.isbn;

-- 3. ISBN 컬럼에 유니크 제약 조건 추가
-- 이 제약 조건이 있어야 ON CONFLICT (isbn) 구문이 작동합니다.
ALTER TABLE childbook_items ADD CONSTRAINT childbook_items_isbn_key UNIQUE (isbn);
