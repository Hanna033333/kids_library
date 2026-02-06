-- 칼데콧 수상작 ISBN 및 표지 이미지 업데이트 (알라딘 API)
-- ISBN 수집 결과: 22/27권 성공
-- 생성일: 2026-02-06

-- 빅: ISBN 9791158364700 (알라딘: 나는 크고 아름다워요 - 2024년 칼데콧 대상 수상작)
UPDATE childbook_items 
SET isbn = '9791158364700',
    image_url = 'https://image.aladin.co.kr/product/34940/64/coversum/k702934463_1.jpg'
WHERE title = '빅' 
  AND curation_tag LIKE '%caldecott%';

-- 핫도그: ISBN 9788961709262 (알라딘: 핫 도그 - 2023 칼데콧 대상 수상작)
UPDATE childbook_items 
SET isbn = '9788961709262',
    image_url = 'https://image.aladin.co.kr/product/31953/73/coversum/8961709267_2.jpg'
WHERE title = '핫도그' 
  AND curation_tag LIKE '%caldecott%';

-- 물냉이: ISBN 9788979381535 (알라딘: 물냉이 - 2022 칼데콧 메달 수상작, 2022 뉴베리 영예상 수상작)
UPDATE childbook_items 
SET isbn = '9788979381535',
    image_url = 'https://image.aladin.co.kr/product/29321/65/coversum/8979381530_2.jpg'
WHERE title = '물냉이' 
  AND curation_tag LIKE '%caldecott%';

-- 우리는 물의 수호자입니다: ISBN 9791168254114 (알라딘: 워터 프로텍터 - 생명의 물을 지키는 사람들 이야기, 2021 칼데콧 대상 수상작)
UPDATE childbook_items 
SET isbn = '9791168254114',
    image_url = 'https://image.aladin.co.kr/product/30345/4/coversum/k312839540_1.jpg'
WHERE title = '우리는 물의 수호자입니다' 
  AND curation_tag LIKE '%caldecott%';

-- 더 언디피티드: ISBN 9788961707978 (알라딘: 우리는 패배하지 않아 - 2020 칼데콧 대상 수상작)
UPDATE childbook_items 
SET isbn = '9788961707978',
    image_url = 'https://image.aladin.co.kr/product/25642/75/coversum/8961707973_1.jpg'
WHERE title = '더 언디피티드' 
  AND curation_tag LIKE '%caldecott%';

-- 안녕, 나의 등대: ISBN 9788949113760 (알라딘: 안녕, 나의 등대)
UPDATE childbook_items 
SET isbn = '9788949113760',
    image_url = 'https://image.aladin.co.kr/product/19052/56/coversum/s912635398_1.jpg'
WHERE title = '안녕, 나의 등대' 
  AND curation_tag LIKE '%caldecott%';

-- 눈보라: ISBN 9788949113692 (알라딘: 세상에서 가장 용감한 소녀 - 2018 칼데콧 대상 수상작)
UPDATE childbook_items 
SET isbn = '9788949113692',
    image_url = 'https://image.aladin.co.kr/product/14969/41/coversum/8949113694_1.jpg'
WHERE title = '눈보라' 
  AND curation_tag LIKE '%caldecott%';

-- 위니를 찾아서: ISBN 9791186621097 (알라딘: 위니를 찾아서 - 2016 칼데콧 대상 수상작)
UPDATE childbook_items 
SET isbn = '9791186621097',
    image_url = 'https://image.aladin.co.kr/product/7848/68/coversum/k252434524_2.jpg'
WHERE title = '위니를 찾아서' 
  AND curation_tag LIKE '%caldecott%';

-- 비클의 모험: ISBN 9791185786353 (알라딘: 비클의 모험 - 상상을 뛰어넘은 여행, 2015 칼데콧 수상작)
UPDATE childbook_items 
SET isbn = '9791185786353',
    image_url = 'https://image.aladin.co.kr/product/5642/22/coversum/6000837808_3.jpg'
WHERE title = '비클의 모험' 
  AND curation_tag LIKE '%caldecott%';

-- 로커모티브: ISBN 9788994407753 (알라딘: 증기기관차 대륙을 달리다 - 2014 칼데콧상 수상작)
UPDATE childbook_items 
SET isbn = '9788994407753',
    image_url = 'https://image.aladin.co.kr/product/23682/75/coversum/8994407758_1.jpg'
WHERE title = '로커모티브' 
  AND curation_tag LIKE '%caldecott%';

-- 이건 내 모자가 아니야: ISBN 9788952786364 (알라딘: 이건 내 모자가 아니야)
UPDATE childbook_items 
SET isbn = '9788952786364',
    image_url = 'https://image.aladin.co.kr/product/14323/29/coversum/895278636x_1.jpg'
WHERE title = '이건 내 모자가 아니야' 
  AND curation_tag LIKE '%caldecott%';

-- 데이지의 공: ISBN 9788983090324 (알라딘: 빨강 파랑 강아지 공 - 2012년 칼데콧메달 수상 그림책)
UPDATE childbook_items 
SET isbn = '9788983090324',
    image_url = 'https://image.aladin.co.kr/product/1840/29/coversum/8983090324_1.jpg'
WHERE title = '데이지의 공' 
  AND curation_tag LIKE '%caldecott%';

-- 아모스 할아버지가 아픈 날: ISBN 9788994041322 (알라딘: 아모스 할아버지가 아픈 날 - 2011년 칼데콧 메달 수상작)
UPDATE childbook_items 
SET isbn = '9788994041322',
    image_url = 'https://image.aladin.co.kr/product/1122/34/coversum/899404132x_3.jpg'
WHERE title = '아모스 할아버지가 아픈 날' 
  AND curation_tag LIKE '%caldecott%';

-- 한밤의 선물: ISBN 9788983090249 (알라딘: 한밤에 우리 집은)
UPDATE childbook_items 
SET isbn = '9788983090249',
    image_url = 'https://image.aladin.co.kr/product/441/75/coversum/8983090243_1.jpg'
WHERE title = '한밤의 선물' 
  AND curation_tag LIKE '%caldecott%';

-- 위고 카브레: ISBN 9788956897936 (알라딘: 위고 카브레 - 자동인형을 깨워라!)
UPDATE childbook_items 
SET isbn = '9788956897936',
    image_url = 'https://image.aladin.co.kr/product/1554/25/coversum/895689793x_1.jpg'
WHERE title = '위고 카브레' 
  AND curation_tag LIKE '%caldecott%';

-- 시간 상자: ISBN 9788952786487 (알라딘: 시간 상자)
UPDATE childbook_items 
SET isbn = '9788952786487',
    image_url = 'https://image.aladin.co.kr/product/13514/88/coversum/8952786483_1.jpg'
WHERE title = '시간 상자' 
  AND curation_tag LIKE '%caldecott%';

-- 안녕, 빠이빠이 창문: ISBN 9788991770287 (알라딘: 안녕 빠이빠이 창문)
UPDATE childbook_items 
SET isbn = '9788991770287',
    image_url = 'https://image.aladin.co.kr/product/63/41/coversum/8991770282_2.jpg'
WHERE title = '안녕, 빠이빠이 창문' 
  AND curation_tag LIKE '%caldecott%';

-- 쌍둥이 빌딩 사이를 걸어간 남자: ISBN 9788990794031 (알라딘: 쌍둥이 빌딩 사이를 걸어간 남자 - 2004년 칼데콧 상 수상작)
UPDATE childbook_items 
SET isbn = '9788990794031',
    image_url = 'https://image.aladin.co.kr/product/51/31/coversum/899079403x_2.jpg'
WHERE title = '쌍둥이 빌딩 사이를 걸어간 남자' 
  AND curation_tag LIKE '%caldecott%';

-- 내 친구 토끼: ISBN 9788958075417 (알라딘: 날마다 말썽 하나 - 2003년 칼데콧 수상작)
UPDATE childbook_items 
SET isbn = '9788958075417',
    image_url = 'https://image.aladin.co.kr/product/4757/44/coversum/8958075414_1.jpg'
WHERE title = '내 친구 토끼' 
  AND curation_tag LIKE '%caldecott%';

-- 아기 돼지 세 마리: ISBN 9788956632209 (알라딘: 아기돼지 세 마리)
UPDATE childbook_items 
SET isbn = '9788956632209',
    image_url = 'https://image.aladin.co.kr/product/219/73/coversum/8956632200_1.jpg'
WHERE title = '아기 돼지 세 마리' 
  AND curation_tag LIKE '%caldecott%';

-- 대통령이 되고 싶다고?: ISBN 9788982816536 (알라딘: 대통령이 되고 싶다고?)
UPDATE childbook_items 
SET isbn = '9788982816536',
    image_url = 'https://image.aladin.co.kr/product/41/40/coversum/8982816534_2.jpg'
WHERE title = '대통령이 되고 싶다고?' 
  AND curation_tag LIKE '%caldecott%';

-- 요셉의 작고 낡은 오버코트: ISBN 9788984880078 (알라딘: 요셉의 작고 낡은 오버코트가 - 베틀리딩클럽 취학전 그림책 1003)
UPDATE childbook_items 
SET isbn = '9788984880078',
    image_url = 'https://image.aladin.co.kr/product/25/3/coversum/8984880078_3.jpg'
WHERE title = '요셉의 작고 낡은 오버코트' 
  AND curation_tag LIKE '%caldecott%';


-- 확인 쿼리
SELECT title, isbn, image_url, pangyo_callno
FROM childbook_items
WHERE curation_tag LIKE '%caldecott%'
ORDER BY title;