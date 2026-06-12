-- 겨울방학2026 태그 중복 데이터 확인 및 정리

-- 1. 중복 확인 쿼리
SELECT title, COUNT(*) as count
FROM childbook_items
WHERE curation_tag = '겨울방학2026'
GROUP BY title
HAVING COUNT(*) > 1
ORDER BY count DESC, title;

-- 2. 전체 겨울방학 도서 확인
SELECT id, title, author, pangyo_callno, curation_tag
FROM childbook_items
WHERE curation_tag = '겨울방학2026'
ORDER BY title, id;

-- 3. 중복 제거 (각 제목별로 가장 작은 ID만 남기고 삭제)
-- 주의: 실행 전 반드시 백업!
DELETE FROM childbook_items
WHERE id IN (
  SELECT id
  FROM (
    SELECT id,
           ROW_NUMBER() OVER (PARTITION BY title ORDER BY id) as rn
    FROM childbook_items
    WHERE curation_tag = '겨울방학2026'
  ) t
  WHERE rn > 1
);

-- 4. 정리 후 확인
SELECT COUNT(*) as total_count, COUNT(DISTINCT title) as unique_titles
FROM childbook_items
WHERE curation_tag = '겨울방학2026';
