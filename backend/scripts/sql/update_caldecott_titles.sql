-- 이미 추가된 칼데콧 수상작 제목 수정 (수식어 제거)
-- 생성일: 2026-02-06

-- 2025: 나의 특별한 도시락
UPDATE childbook_items
SET title = '나의 특별한 도시락'
WHERE isbn = '9791169942874';

-- 2021: 워터 프로텍터
UPDATE childbook_items
SET title = '워터 프로텍터'
WHERE isbn = '9791168254114';

-- 2020: 우리는 패배하지 않아
UPDATE childbook_items
SET title = '우리는 패배하지 않아'
WHERE isbn = '9788961707978';

-- 2014: 증기기관차 대륙을 달리다
UPDATE childbook_items
SET title = '증기기관차 대륙을 달리다'
WHERE isbn = '9788994407753';

-- 2012: 빨강 파랑 강아지 공
UPDATE childbook_items
SET title = '빨강 파랑 강아지 공'
WHERE isbn = '9788983090324';

-- 2006: 할아버지 댁 창문
UPDATE childbook_items
SET title = '할아버지 댁 창문'
WHERE isbn = '9791125304562';

-- 확인 쿼리
SELECT title, isbn FROM childbook_items 
WHERE isbn IN (
  '9791169942874', 
  '9791168254114', 
  '9788961707978', 
  '9788994407753', 
  '9788983090324', 
  '9791125304562'
);
