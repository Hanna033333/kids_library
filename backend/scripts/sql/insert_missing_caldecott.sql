-- 추가된 칼데콧 수상작 (사용자 제공 ISBN 기반)
-- 생성일: 2026-02-06

-- 2025년: 나의 특별한 도시락 - 2025 칼데콧 아너상 수상작
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('나의 특별한 도시락', '체리 모 (지은이), 노은정 (옮긴이)', '오늘책', '9791169942874', 'https://image.aladin.co.kr/product/36801/79/cover200/k752030806_1.jpg', NULL, 'caldecott', '그림책', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2021년: 워터 프로텍터 - 생명의 물을 지키는 사람들 이야기, 2021 칼데콧 대상 수상작
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('워터 프로텍터', '캐롤 린드스트롬 (지은이), 미카엘라 고드 (그림), 노은정 (옮긴이)', '오늘책', '9791168254114', 'https://image.aladin.co.kr/product/30345/4/cover200/k312839540_1.jpg', NULL, 'caldecott', '그림책', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2020년: 우리는 패배하지 않아 - 2020 칼데콧 대상 수상작
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('우리는 패배하지 않아', '콰미 알렉산더 (지은이), 카디르 넬슨 (그림), 조고은 (옮긴이)', '보물창고', '9788961707978', 'https://image.aladin.co.kr/product/25642/75/cover200/8961707973_1.jpg', NULL, 'caldecott', '그림책', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2014년: 증기기관차 대륙을 달리다 - 2014 칼데콧상 수상작
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('증기기관차 대륙을 달리다', '브라이언 플로카 (지은이), 유만선 (옮긴이)', '너머학교', '9788994407753', 'https://image.aladin.co.kr/product/23682/75/cover200/8994407758_1.jpg', NULL, 'caldecott', '그림책', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2012년: 빨강 파랑 강아지 공 - 2012년 칼데콧메달 수상 그림책
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('빨강 파랑 강아지 공', '크리스 라쉬카 (지은이)', '지양어린이', '9788983090324', 'https://image.aladin.co.kr/product/1840/29/cover200/8983090324_1.jpg', NULL, 'caldecott', '그림책', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2006년: 할아버지 댁 창문 - 인성동화 라 - ③
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('할아버지 댁 창문', '노턴 저스터 (글), 크리스 라시카 (그림), 금동이책 (옮긴이)', '엔이키즈', '9791125304562', 'https://image.aladin.co.kr/product/4843/56/cover200/1125304561_1.jpg', NULL, 'caldecott', '그림책', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);
