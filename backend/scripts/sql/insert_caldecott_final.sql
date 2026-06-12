-- 칼데콧 수상작 데이터 삽입 (2000-2026)
-- 생성일: 2026-02-04
-- 총 27권 (ISBN: 20권, 청구기호: 17권)

-- 2026년: Fireworks
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('Fireworks', '매튜 버지스 (글), 카티아 치엔 (그림)', '책쓰는밤', '9791194853404', 'https://image.aladin.co.kr/product/38551/79/cover500/k442135756_1.jpg', 'J 843-R888c-v.6', 'caldecott', '동화', '7세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2024년: 빅
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('빅', '바시티 해리슨', '대원씨아이(만화)', '9791142341595', 'https://image.aladin.co.kr/product/38442/8/cover500/k372135894_1.jpg', '942.07-ㅇ235ㅂ', 'caldecott', '동화', '7세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2023년: 핫도그
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('핫도그', '더그 살라티', '레시피팩토리', '9791185473895', 'https://image.aladin.co.kr/product/27833/74/cover500/k042734674_2.jpg', '843-ㅅ9545ㅅ', 'caldecott', '동화', '7세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2022년: 물냉이 (2022 칼데콧 메달 수상작)
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('물냉이', '안드레아 왕 (지은이), 제이슨 친 (그림), 장미란 (옮긴이)', '다산기획', '9788979381535', 'https://image.aladin.co.kr/product/29321/65/cover500/8979381530_2.jpg', '유 808.9-ㄷ99ㄷ-33', 'caldecott', '동화', '7세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2019년: 안녕, 나의 등대
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('안녕, 나의 등대', '소피 블랙올 (지은이), 정회성 (옮긴이)', '비룡소', '9788949113760', 'https://image.aladin.co.kr/product/19052/56/cover500/s912635398_1.jpg', '유 808.9-ㅂ966ㅂ-259', 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2018년: 눈보라
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('눈보라', '매튜 코델', '창비', '9788936455606', 'https://image.aladin.co.kr/product/25967/85/cover500/8936455605_2.jpg', 'DVD 688.6-ㅅ724ㅇ-4', 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2017년: 빛나는 아이
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('빛나는 아이', '자바카 셉토', '명주', '9788969850386', 'https://image.aladin.co.kr/product/37772/42/cover500/8969850384_1.jpg', '아 082-ㅅ724스-14', 'caldecott', '인물', '9세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2016년: 위니를 찾아서 (2016 칼데콧 대상 수상작)
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('위니를 찾아서', '린지 매틱 (글), 소피 블랙올 (그림), 정회성 (옮긴이)', '창비', '9791186621097', 'https://image.aladin.co.kr/product/7848/68/cover500/k252434524_2.jpg', '아 843-ㅅ378ㅇ', 'caldecott', '역사', '7세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2015년: 비클의 모험 (2015 칼데콧 수상작)
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('비클의 모험', '댄 샌탯 (지은이), 고정아 (옮긴이)', '아르볼', '9791185786353', 'https://image.aladin.co.kr/product/5642/22/cover500/6000837808_3.jpg', '유 843-ㅅ195ㅂ', 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2013년: 이건 내 모자가 아니야 (2013 칼데콧 상 수상작)
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('이건 내 모자가 아니야', '존 클라센 (지은이), 서남희 (옮긴이)', '시공주니어', '9788952786364', 'https://image.aladin.co.kr/product/14323/29/cover500/895278636x_1.jpg', '유 808.9-ㄴ59ㅅ-231', 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2011년: 아모스 할아버지가 아픈 날
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('아모스 할아버지가 아픈 날', '필립 C. 스테드 (지은이), 에린 E. 스테드 (그림), 강무홍 (옮긴이)', '주니어RHK(주니어랜덤)', '9788925579146', 'https://image.aladin.co.kr/product/28505/96/cover500/8925579146_1.jpg', '유 808.9-ㅂ778ㅈ-1-1', 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2010년: 사자와 생쥐 (2010년 칼데콧 상 수상작)
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('사자와 생쥐', '제리 핑크니 (지은이), 윤한구 (옮긴이)', '별천지(열린책들)', '9788994041162', 'https://image.aladin.co.kr/product/655/41/cover500/8994041168_1.jpg', '유 375.1-ㅅ388ㄱ-3=2', 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2009년: 한밤의 선물
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('한밤의 선물', '수잔 마리 스완슨 (글), 베스 크롬스 (그림)', '봄봄출판사', '9788991742659', 'https://image.aladin.co.kr/product/5192/7/cover500/8991742653_1.jpg', '유 808.9-ㅂ882ㅂ-44', 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2008년: 위고 카브레 (2008년 칼데콧 상 수상작)
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('위고 카브레', '브라이언 셀즈닉 (지은이), 이은정 (옮긴이)', '뜰book', '9788956897936', 'https://image.aladin.co.kr/product/1554/25/cover500/895689793x_1.jpg', '아 843-ㅅ396ㅇ2', 'caldecott', '소설', '9세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2007년: 시간 상자 (2007년 칼데콧 상 수상작)
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('시간 상자', '데이비드 위즈너 (지은이)', '시공주니어', '9788952786487', 'https://image.aladin.co.kr/product/13514/88/cover500/8952786483_1.jpg', NULL, 'caldecott', '동화', '7세부터', true)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2005년: 달을 먹은 아기 고양이 (2005년 칼데콧상 수상작)
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('달을 먹은 아기 고양이', '케빈 헹크스 (지은이), 맹주열 (옮긴이)', '비룡소', '9788949111438', 'https://image.aladin.co.kr/product/56/67/cover500/8949111438_1.jpg', '유 808.9-ㅂ966ㅂ-145=3', 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2004년: 쌍둥이 빌딩 사이를 걸어간 남자 (2004년 칼데콧 상 수상작)
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('쌍둥이 빌딩 사이를 걸어간 남자', '모디캐이 저스타인 (지은이), 신형건 (옮긴이)', '보물창고', '9788990794031', 'https://image.aladin.co.kr/product/51/31/cover500/899079403x_2.jpg', '유 808.9-ㄱ571ㅂ-1', 'caldecott', '인물', '7세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2003년: 내 친구 토끼
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('내 친구 토끼', '에릭 로만', '엄마마음', '9791162280393', 'https://image.aladin.co.kr/product/27547/9/cover500/k492733493_1.jpg', NULL, 'caldecott', '동화', '5세부터', true)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2002년: 아기 돼지 세 마리
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('아기 돼지 세 마리', '데이비드 위즈너', '비룡소', '9788949100760', 'https://image.aladin.co.kr/product/26/66/cover500/8949100762_1.jpg', NULL, 'caldecott', '동화', '5세부터', true)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2001년: 대통령이 되고 싶다고?
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('대통령이 되고 싶다고?', '주디스 세인트 조지 (글), 데이비드 스몰 (그림), 김연수 (옮긴이)', '문학동네', '9788982816536', 'https://image.aladin.co.kr/product/41/40/cover500/8982816534_2.jpg', NULL, 'caldecott', '사회', '7세부터', true)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2000년: 요셉의 작고 낡은 오버코트
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('요셉의 작고 낡은 오버코트가', '심스 태백 (지은이), 김정희 (옮긴이)', '베틀북', '9788984880078', 'https://image.aladin.co.kr/product/25/3/cover500/8984880078_3.jpg', '유 808.9-ㄱ571베-4', 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  pangyo_callno = COALESCE(EXCLUDED.pangyo_callno, childbook_items.pangyo_callno),
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 확인 쿼리
SELECT title, author, isbn, pangyo_callno, image_url, is_hidden
FROM childbook_items
WHERE curation_tag LIKE '%caldecott%'
ORDER BY title;
-- 추가된 칼데콧 수상작 (사용자 제공 ISBN 기반)
-- 생성일: 2026-02-06

-- 2025년: 나의 특별한 도시락 - 2025 칼데콧 아너상 수상작
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('나의 특별한 도시락', '체리 모 (지은이), 노은정 (옮긴이)', '오늘책', '9791169942874', 'https://image.aladin.co.kr/product/36801/79/cover200/k752030806_1.jpg', NULL, 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2021년: 워터 프로텍터 - 생명의 물을 지키는 사람들 이야기, 2021 칼데콧 대상 수상작
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('워터 프로텍터', '캐롤 린드스트롬 (지은이), 미카엘라 고드 (그림), 노은정 (옮긴이)', '오늘책', '9791168254114', 'https://image.aladin.co.kr/product/30345/4/cover200/k312839540_1.jpg', NULL, 'caldecott', '사회', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2020년: 우리는 패배하지 않아 - 2020 칼데콧 대상 수상작
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('우리는 패배하지 않아', '콰미 알렉산더 (지은이), 카디르 넬슨 (그림), 조고은 (옮긴이)', '보물창고', '9788961707978', 'https://image.aladin.co.kr/product/25642/75/cover200/8961707973_1.jpg', NULL, 'caldecott', '인물', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2014년: 증기기관차 대륙을 달리다 - 2014 칼데콧상 수상작
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('증기기관차 대륙을 달리다', '브라이언 플로카 (지은이), 유만선 (옮긴이)', '너머학교', '9788994407753', 'https://image.aladin.co.kr/product/23682/75/cover200/8994407758_1.jpg', NULL, 'caldecott', '역사', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2012년: 빨강 파랑 강아지 공 - 2012년 칼데콧메달 수상 그림책
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('빨강 파랑 강아지 공', '크리스 라쉬카 (지은이)', '지양어린이', '9788983090324', 'https://image.aladin.co.kr/product/1840/29/cover200/8983090324_1.jpg', NULL, 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);

-- 2006년: 할아버지 댁 창문 - 인성동화 라 - ③
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('할아버지 댁 창문', '노턴 저스터 (글), 크리스 라시카 (그림), 금동이책 (옮긴이)', '엔이키즈', '9791125304562', 'https://image.aladin.co.kr/product/4843/56/cover200/1125304561_1.jpg', NULL, 'caldecott', '동화', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);
