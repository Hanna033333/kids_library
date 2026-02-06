-- 모든 책 이미지 URL을 고화질(cover500)로 일괄 업데이트
-- coversum(약 85px) -> cover500(500px)

UPDATE childbook_items 
SET image_url = REPLACE(image_url, '/coversum/', '/cover500/')
WHERE image_url LIKE '%/coversum/%';

-- 확인 쿼리
SELECT title, image_url 
FROM childbook_items 
WHERE image_url LIKE '%/cover500/%' 
ORDER BY title
LIMIT 10;
