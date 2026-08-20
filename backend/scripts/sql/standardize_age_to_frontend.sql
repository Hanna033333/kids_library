-- ============================================================
-- standardize_age_to_frontend.sql
-- DB의 age 컬럼을 프론트엔드 표준 연령 키로 전면 마이그레이션
-- 프론트엔드 표준: '0-3', '4-7', '8-12', '13+'
-- ============================================================

-- 1) 0~3세 그룹
UPDATE childbook_items
SET age = '0-3'
WHERE age IN ('0세부터', '1세부터', '2세부터', '3세부터');

-- 2) 4~7세 그룹
UPDATE childbook_items
SET age = '4-7'
WHERE age IN ('4세부터', '5세부터', '6세부터', '7세부터')
   OR age ILIKE '%유아%';

-- 3) 8~12세 그룹
UPDATE childbook_items
SET age = '8-12'
WHERE age IN ('8세부터', '9세부터', '10세부터', '11세부터', '12세부터');

-- 4) 13세 이상 그룹
UPDATE childbook_items
SET age = '13+'
WHERE age IN ('13세부터', '14세부터', '15세부터', '16세부터', '17세부터', '18세부터', 'teen');

-- 5) 아동 서비스 대상 외 도서 숨김 처리
UPDATE childbook_items
SET is_hidden = true
WHERE age IN ('교사·학부모');

-- 6) 남은 비표준 값 확인 (결과가 비어있으면 완전 정제 완료)
SELECT DISTINCT age, COUNT(*) AS cnt
FROM childbook_items
WHERE age NOT IN ('0-3', '4-7', '8-12', '13+')
  AND age IS NOT NULL
  AND (is_hidden IS NULL OR is_hidden = false)
GROUP BY age
ORDER BY cnt DESC;
