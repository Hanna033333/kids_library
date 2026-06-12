-- 수동 입력 ISBN 업데이트 (알라딘 메타데이터 포함)
-- 처리 건수: 3권
-- 생성일: 2026-01-19

-- 책 요정 도도 : 도서관을 구해 줘!
UPDATE childbook_items 
SET isbn = '9791194098034',
    image_url = 'https://image.aladin.co.kr/product/36094/48/cover200/k292038865_2.jpg',
    publisher = '파스텔하우스'
WHERE title = '책 요정 도도 : 도서관을 구해 줘!' 
  AND curation_tag = '겨울방학2026';

-- 불안이 사르르 사라지는 그림책 : 작은 일에도 걱정부터 앞서는 아이를 위한 마음 사용법
UPDATE childbook_items 
SET isbn = '9791140713585',
    image_url = 'https://image.aladin.co.kr/product/36581/52/cover200/k262039452_1.jpg',
    publisher = '길벗'
WHERE title = '불안이 사르르 사라지는 그림책 : 작은 일에도 걱정부터 앞서는 아이를 위한 마음 사용법' 
  AND curation_tag = '겨울방학2026';

-- 일곱 빛깔 감정 나라 : 내 안의 다채로운 감정과 만나는 곳
UPDATE childbook_items 
SET isbn = '9791168272941',
    image_url = 'https://image.aladin.co.kr/product/36415/55/cover200/k122039990_1.jpg',
    publisher = '데이스타'
WHERE title = '일곱 빛깔 감정 나라 : 내 안의 다채로운 감정과 만나는 곳' 
  AND curation_tag = '겨울방학2026';
