BEGIN;

-- 1. 기존 올바른 책(11154)에 caldecott 태그 추가 (기존 태그 유지)
UPDATE childbook_items
SET curation_tag = CASE 
    WHEN curation_tag IS NULL OR curation_tag = '' THEN 'caldecott'
    WHEN curation_tag LIKE '%caldecott%' THEN curation_tag
    ELSE curation_tag || ', caldecott'
END
WHERE id = 11154;

-- 2. 잘못된 정보가 섞인 중복 레코드(11408) 삭제
DELETE FROM childbook_items WHERE id = 11408;

COMMIT;
