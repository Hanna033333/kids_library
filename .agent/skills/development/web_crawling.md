# 웹 크롤링 가이드: 판교도서관 청구기호 수집

## 📋 개요

판교도서관(성남시립도서관) 웹사이트에서 도서 청구기호를 자동으로 수집하는 웹 크롤링 프로세스입니다.

---

## 🎯 사용 사례

### 언제 사용하나?
- 새로운 도서 목록(CSV/Excel)을 받았을 때
- 데이터베이스에 청구기호가 없는 책들이 있을 때
- 겨울방학/여름방학 등 시즌별 추천 도서 추가 시

### 기대 효과
- 수동 검색 대비 **시간 절약** (40권 기준 약 1시간 → 2분)
- **정확한 청구기호** 자동 수집
- **일괄 업데이트** SQL 자동 생성

---

## 🏗️ 시스템 구조

### 판교도서관 웹사이트 분석

**공식 URL**: https://www.snlib.go.kr/pg/index.do

**검색 API 엔드포인트**:
```
https://www.snlib.go.kr/pg/plusSearchResultList.do
```

**검색 파라미터**:
```python
params = {
    'searchKeyword': '책 제목',
    'searchType': 'SIMPLE',
    'searchCategory': 'BOOK',
    'searchLibraryArr': 'MP',  # 판교도서관 코드
    'searchKey': 'ALL',
    'topSearchType': 'BOOK'
}
```

**HTML 구조**:
```html
<ul class="resultList">
  <li>
    <dl>
      <dt><a>책 제목</a></dt>
      <dd>저자 : ...</dd>
      <dd>발행자: ...</dd>
      <dd>청구기호: 유 813.8-ㄱ985ㄴ</dd>  <!-- 여기! -->
    </dl>
  </li>
</ul>
```

**CSS 셀렉터**:
- 검색 결과 리스트: `ul.resultList > li`
- 청구기호: `dd` 요소 중 "청구기호:" 텍스트 포함

---

## 🔧 구현 방법

### 1. 필수 라이브러리

```python
import requests
from bs4 import BeautifulSoup
import json
import time
import re
```

### 2. 크롤링 스크립트 템플릿

```python
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.snlib.go.kr/pg/plusSearchResultList.do"

def crawl_callno(title, author=''):
    """판교도서관에서 청구기호 검색"""
    
    params = {
        'searchKeyword': title,
        'searchType': 'SIMPLE',
        'searchCategory': 'BOOK',
        'searchLibraryArr': 'MP',  # 판교도서관
        'searchKey': 'ALL',
        'topSearchType': 'BOOK'
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 첫 번째 검색 결과
        result_list = soup.select('ul.resultList > li')
        
        if result_list:
            first_result = result_list[0]
            
            # 청구기호 찾기
            dd_elements = first_result.select('dl dd')
            for dd in dd_elements:
                text = dd.get_text(strip=True)
                if '청구기호:' in text:
                    callno = text.replace('청구기호:', '').strip()
                    # 불필요한 텍스트 제거
                    callno = callno.split('위치출력')[0].strip()
                    return callno
        
        return None
        
    except Exception as e:
        print(f"에러: {e}")
        return None

# 사용 예시
callno = crawl_callno("나는 오늘도 감정식당에 가요")
print(f"청구기호: {callno}")
```

### 3. 청구기호 데이터 정제

크롤링한 청구기호에는 불필요한 메타데이터가 포함되어 있을 수 있습니다:

```python
def clean_callno(raw_callno):
    """청구기호 정제"""
    if not raw_callno:
        return None
    
    # "저자 : ... 발행자: ... 발행연도: YYYY 청구기호" 패턴
    parts = raw_callno.split('발행연도:')
    if len(parts) >= 2:
        after_year = parts[-1].strip()
        # 연도 제거 (4자리 숫자)
        callno = re.sub(r'^\d{4}\s+', '', after_year)
        return callno.strip()
    
    return raw_callno.strip()
```

**예시**:
```
입력: "저자 : 김현태 글 ; 오숙진 그림발행자: 그린북발행연도: 2025 유 813.8-ㄹ434-11"
출력: "유 813.8-ㄹ434-11"
```

---

## 📝 전체 워크플로우

### Step 1: 도서 목록 준비

CSV 파일 형식:
```csv
title,author,publisher
나는 오늘도 감정식당에 가요,김현태,그린북
창덕궁에 불이 꺼지면,최정혜,책읽는곰
```

### Step 2: 크롤링 실행

```python
import json
import csv
import time

# CSV 읽기
books = []
with open('books.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    books = list(reader)

# 크롤링
results = []
for i, book in enumerate(books, 1):
    print(f"[{i}/{len(books)}] {book['title']}")
    
    callno = crawl_callno(book['title'], book['author'])
    
    if callno:
        callno = clean_callno(callno)
        results.append({
            'title': book['title'],
            'callno': callno,
            'status': 'success'
        })
        print(f"  ✅ {callno}")
    else:
        results.append({
            'title': book['title'],
            'callno': None,
            'status': 'not_found'
        })
        print(f"  ❌ 검색 결과 없음")
    
    # 서버 부하 방지
    time.sleep(1.5)

# 결과 저장
with open('callno_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### Step 3: SQL 생성

```python
# UPDATE SQL 생성
sql_lines = []
sql_lines.append("-- 청구기호 업데이트")
sql_lines.append("")

for result in results:
    if result['status'] == 'success' and result['callno']:
        title_escaped = result['title'].replace("'", "''")
        callno_escaped = result['callno'].replace("'", "''")
        
        sql = f"""UPDATE childbook_items 
SET pangyo_callno = '{callno_escaped}'
WHERE title = '{title_escaped}';
"""
        sql_lines.append(f"-- {result['title']}")
        sql_lines.append(sql)

with open('update_callno.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))
```

### Step 4: 데이터베이스 업데이트

Supabase SQL Editor에서 `update_callno.sql` 실행

---

## ⚠️ 주의사항

### 1. 서버 부하 방지

**필수**: 요청 간 1-2초 대기
```python
time.sleep(1.5)  # 1.5초 대기
```

### 2. 신간 도서 미등록

**문제**: 2025년 신간은 도서관에 아직 등록되지 않았을 수 있음

**해결**:
- 실패한 책 목록을 CSV로 저장
- 1-2주 후 재크롤링
- 또는 수동으로 청구기호 확인

### 3. 검색 결과 정확도

**문제**: 동명이서(같은 제목의 다른 책)가 있을 수 있음

**해결**:
- 저자명으로 2차 필터링
- 출판사 정보로 3차 검증
- 결과를 수동으로 확인

```python
# 저자명으로 필터링 예시
author_name = author.split()[0]  # 첫 번째 저자명
if author_name and author_name in result_author:
    # 매칭 성공
    pass
```

---

## 📊 성공률 향상 팁

### 1. 제목 정규화

```python
def normalize_title(title):
    """제목 정규화"""
    # 괄호 제거
    title = re.sub(r'\([^)]*\)', '', title)
    # 부제 제거
    title = title.split(':')[0]
    return title.strip()
```

### 2. 재시도 로직

```python
def crawl_with_retry(title, max_retries=3):
    """재시도 로직"""
    for attempt in range(max_retries):
        try:
            result = crawl_callno(title)
            if result:
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 지수 백오프
            else:
                raise
    return None
```

### 3. 캐싱

```python
import pickle

# 결과 캐싱
cache = {}
try:
    with open('callno_cache.pkl', 'rb') as f:
        cache = pickle.load(f)
except:
    pass

def crawl_with_cache(title):
    if title in cache:
        return cache[title]
    
    result = crawl_callno(title)
    cache[title] = result
    
    with open('callno_cache.pkl', 'wb') as f:
        pickle.dump(cache, f)
    
    return result
```

---

## 🎓 실전 예시: 겨울방학 도서 40권

### 결과 요약
- **총**: 40권
- **성공**: 22권 (55%)
- **실패**: 18권 (45% - 신간 미등록)

### 생성된 파일
1. `winter_books_callno_results.json` - 크롤링 결과
2. `update_winter_callno_clean.sql` - UPDATE SQL (22권)
3. `winter_books_missing_callno.csv` - 실패 목록 (18권)

### 실행 시간
- 크롤링: 약 2분 (40권 × 1.5초 + 네트워크 시간)
- SQL 생성: 1초 미만

---

## 🔍 트러블슈팅

### 문제 1: 연결 타임아웃

**증상**: `requests.exceptions.Timeout`

**해결**:
```python
response = requests.get(BASE_URL, params=params, timeout=15)  # 타임아웃 증가
```

### 문제 2: 인코딩 에러

**증상**: 한글이 깨짐

**해결**:
```python
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')
```

### 문제 3: 중복 데이터

**증상**: 같은 책이 여러 번 INSERT됨

**해결**:
```sql
-- 중복 제거
DELETE FROM childbook_items
WHERE id IN (
  SELECT id FROM (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY title ORDER BY id) as rn
    FROM childbook_items
    WHERE curation_tag = '겨울방학2026'
  ) t
  WHERE rn > 1
);
```

---

## 📚 참고 자료

### 관련 파일
- `backend/crawl_pangyo_callno_v2.py` - 크롤링 스크립트
- `backend/clean_callno_data.py` - 데이터 정제 스크립트
- `backend/export_missing_books.py` - 실패 목록 CSV 생성

### 외부 문서
- [BeautifulSoup 공식 문서](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests 라이브러리](https://requests.readthedocs.io/)
- [성남시립도서관](https://www.snlib.go.kr/)

---

## ✅ 체크리스트

크롤링 작업 시 확인 사항:

- [ ] 도서 목록 CSV/JSON 파일 준비
- [ ] 크롤링 스크립트 실행 (서버 부하 주의)
- [ ] 결과 JSON 파일 확인
- [ ] 청구기호 데이터 정제
- [ ] UPDATE SQL 생성
- [ ] 실패 목록 CSV 생성 (재시도용)
- [ ] Supabase에서 SQL 실행
- [ ] 데이터베이스 확인 쿼리 실행
- [ ] 중복 데이터 확인 및 제거
