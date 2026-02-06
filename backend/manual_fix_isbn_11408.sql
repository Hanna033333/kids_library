UPDATE childbook_items
SET isbn = '9788961709262' -- 새 ISBN
WHERE id = 11408; -- title이 아니라 ID를 기준으로 조회해야 함
