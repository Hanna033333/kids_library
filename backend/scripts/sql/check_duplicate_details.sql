-- 중복된 ISBN을 가진 데이터 조회 쿼리
-- 확인이 필요한 ISBN: 9788950998370, 9788958282792, 9788986621785

SELECT 
    id,
    title,
    isbn,
    publisher,
    pangyo_callno,
    image_url,
    created_at
FROM 
    childbook_items
WHERE 
    isbn IN ('9788950998370', '9788958282792', '9788986621785')
ORDER BY 
    isbn, id;
