-- 겨울방학 도서 이미지 화질 개선
-- coversum (85px) → cover500 (500px) 변경
-- 실행일: 2026-01-20

-- 알라딘 이미지 URL에서 coversum을 cover500으로 일괄 변경
UPDATE childbook_items 
SET image_url = REPLACE(image_url, '/coversum/', '/cover500/')
WHERE curation_tag = '겨울방학2026'
  AND image_url LIKE '%/coversum/%';

-- 확인 쿼리: 변경된 이미지 URL 확인
SELECT id, title, image_url
FROM childbook_items
WHERE curation_tag = '겨울방학2026'
ORDER BY id;
