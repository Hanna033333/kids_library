-- 칼데콧 수상작 중복 해결 및 데이터 병합
-- 생성일: 2026-02-06
-- 업데이트: '빅' 정보 보완
UPDATE childbook_items 
SET isbn = '9791158364700',
    image_url = 'https://image.aladin.co.kr/product/34940/64/coversum/k702934463_1.jpg'
WHERE title = '빅' 
  AND curation_tag LIKE '%caldecott%';

-- 업데이트: '핫도그' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '9788961709262',
    image_url = 'https://image.aladin.co.kr/product/31953/73/coversum/8961709267_2.jpg'
WHERE title = '핫도그' 
  AND curation_tag LIKE '%caldecott%';
-- 업데이트: '물냉이' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '9788979381535',
    image_url = 'https://image.aladin.co.kr/product/29321/65/coversum/8979381530_2.jpg'
WHERE title = '물냉이' 
  AND curation_tag LIKE '%caldecott%';
-- 업데이트: '우리는 물의 수호자입니다' 정보 보완
UPDATE childbook_items 
SET isbn = '9791168254114',
    image_url = 'https://image.aladin.co.kr/product/30345/4/coversum/k312839540_1.jpg'
WHERE title = '우리는 물의 수호자입니다' 
  AND curation_tag LIKE '%caldecott%';

-- 업데이트: '더 언디피티드' 정보 보완
UPDATE childbook_items 
SET isbn = '9788961707978',
    image_url = 'https://image.aladin.co.kr/product/25642/75/coversum/8961707973_1.jpg'
WHERE title = '더 언디피티드' 
  AND curation_tag LIKE '%caldecott%';

-- 업데이트: '안녕, 나의 등대' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '9788949113760',
    image_url = 'https://image.aladin.co.kr/product/19052/56/coversum/s912635398_1.jpg'
WHERE title = '안녕, 나의 등대' 
  AND curation_tag LIKE '%caldecott%';
-- 병합: 기존 '세상에서 가장 용감한 소녀'에 태그 추가
UPDATE childbook_items
SET curation_tag = '어린이도서연구회, caldecott'
WHERE id = 9434;
-- 삭제: 잘못된 정보로 생성된 '눈보라' 삭제
DELETE FROM childbook_items
WHERE title = '눈보라' AND curation_tag LIKE '%caldecott%';

-- 업데이트: '위니를 찾아서' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '9791186621097',
    image_url = 'https://image.aladin.co.kr/product/7848/68/coversum/k252434524_2.jpg'
WHERE title = '위니를 찾아서' 
  AND curation_tag LIKE '%caldecott%';
-- 업데이트: '비클의 모험' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '9791185786353',
    image_url = 'https://image.aladin.co.kr/product/5642/22/coversum/6000837808_3.jpg'
WHERE title = '비클의 모험' 
  AND curation_tag LIKE '%caldecott%';
-- 업데이트: '로커모티브' 정보 보완
UPDATE childbook_items 
SET isbn = '9788994407753',
    image_url = 'https://image.aladin.co.kr/product/23682/75/coversum/8994407758_1.jpg'
WHERE title = '로커모티브' 
  AND curation_tag LIKE '%caldecott%';

-- 업데이트: '이건 내 모자가 아니야' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '9788952786364',
    image_url = 'https://image.aladin.co.kr/product/14323/29/coversum/895278636x_1.jpg'
WHERE title = '이건 내 모자가 아니야' 
  AND curation_tag LIKE '%caldecott%';
-- 업데이트: '데이지의 공' 정보 보완
UPDATE childbook_items 
SET isbn = '9788983090324',
    image_url = 'https://image.aladin.co.kr/product/1840/29/coversum/8983090324_1.jpg'
WHERE title = '데이지의 공' 
  AND curation_tag LIKE '%caldecott%';

-- 업데이트: '아모스 할아버지가 아픈 날' 정보 보완
UPDATE childbook_items 
SET isbn = '9788994041322',
    image_url = 'https://image.aladin.co.kr/product/1122/34/coversum/899404132x_3.jpg'
WHERE title = '아모스 할아버지가 아픈 날' 
  AND curation_tag LIKE '%caldecott%';

-- 업데이트: '한밤의 선물' 정보 보완
UPDATE childbook_items 
SET isbn = '9788983090249',
    image_url = 'https://image.aladin.co.kr/product/441/75/coversum/8983090243_1.jpg'
WHERE title = '한밤의 선물' 
  AND curation_tag LIKE '%caldecott%';

-- 업데이트: '위고 카브레' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '9788956897936',
    image_url = 'https://image.aladin.co.kr/product/1554/25/coversum/895689793x_1.jpg'
WHERE title = '위고 카브레' 
  AND curation_tag LIKE '%caldecott%';
-- 업데이트: '시간 상자' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '9788952786487',
    image_url = 'https://image.aladin.co.kr/product/13514/88/coversum/8952786483_1.jpg'
WHERE title = '시간 상자' 
  AND curation_tag LIKE '%caldecott%';
-- 업데이트: '안녕, 빠이빠이 창문' 정보 보완
UPDATE childbook_items 
SET isbn = '9788991770287',
    image_url = 'https://image.aladin.co.kr/product/63/41/coversum/8991770282_2.jpg'
WHERE title = '안녕, 빠이빠이 창문' 
  AND curation_tag LIKE '%caldecott%';

-- 업데이트: '쌍둥이 빌딩 사이를 걸어간 남자' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '9788990794031',
    image_url = 'https://image.aladin.co.kr/product/51/31/coversum/899079403x_2.jpg'
WHERE title = '쌍둥이 빌딩 사이를 걸어간 남자' 
  AND curation_tag LIKE '%caldecott%';
-- 업데이트: '내 친구 토끼' 정보 보완
UPDATE childbook_items 
SET isbn = '9788958075417',
    image_url = 'https://image.aladin.co.kr/product/4757/44/coversum/8958075414_1.jpg'
WHERE title = '내 친구 토끼' 
  AND curation_tag LIKE '%caldecott%';

-- 업데이트: '아기 돼지 세 마리' 정보 보완
UPDATE childbook_items 
SET isbn = '9788956632209',
    image_url = 'https://image.aladin.co.kr/product/219/73/coversum/8956632200_1.jpg'
WHERE title = '아기 돼지 세 마리' 
  AND curation_tag LIKE '%caldecott%';

-- 업데이트: '대통령이 되고 싶다고?' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '9788982816536',
    image_url = 'https://image.aladin.co.kr/product/41/40/coversum/8982816534_2.jpg'
WHERE title = '대통령이 되고 싶다고?' 
  AND curation_tag LIKE '%caldecott%';
-- 기존 '요셉의 작고 낡은 오버코트가' (ID 11426)는 이미 caldecott 태그 보유
-- 삭제: 잘못된 정보로 생성된 '요셉의 작고 낡은 오버코트' 삭제
DELETE FROM childbook_items
WHERE title = '요셉의 작고 낡은 오버코트' AND curation_tag LIKE '%caldecott%';
