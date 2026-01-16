# 도서관 청구기호 스크래핑 작업 가이드 (Scraping Work)

이 문서는 판교도서관 및 송파어린이도서관 등 다중 도서관의 청구기호를 수집하는 시스템에 대해 설명합니다.

## 1. 시스템 구조

### 데이터베이스 (Supabase)
기존에는 `childbook_items` 테이블에 `pangyo_callno` 등 컬럼을 직접 추가했으나, 도서관이 늘어남에 따라 **별도의 테이블로 분리**하여 관리합니다.

- **`childbook_items`**: 책 기본 정보 (제목, 저자, ISBN 등)
- **`book_library_info`**: 도서관별 청구기호 정보 (1:N 관계)

#### `book_library_info` 테이블 스키마
| 컬럼명 | 타입 | 설명 |
|---|---|---|
| `id` | BigInt | PK |
| `book_id` | BigInt | FK (`childbook_items.id`) |
| `library_name` | Text | 도서관 이름 (예: '판교도서관', '송파어린이도서관') |
| `callno` | Text | 수집된 청구기호 |
| `created_at` | Timestamp | 생성일 |

---

## 2. 스크립트 사용법

스크래핑 스크립트는 `backend` 폴더 내의 `scrape_callno_from_web.py`입니다.

### 기본 실행
```powershell
cd "c:\Users\skplanet\Desktop\kids library\backend"
python scrape_callno_from_web.py --library "도서관이름" --limit 개수
```

### 도서관별 예시
**1. 송파어린이도서관 (신규)**
```powershell
python scrape_callno_from_web.py --library "송파어린이도서관" --limit 100
```

**2. 판교도서관 (기존)**
```powershell
python scrape_callno_from_web.py --library "판교도서관" --limit 100
```

---

## 3. 코드 구조 (`scrape_callno_from_web.py`)

스크립트는 다음과 같이 도서관별 로직이 분리되어 있어 확장이 용이합니다.

1.  **`LIBRARY_SEARCH_FUNCS`**: 도서관 이름과 검색 함수를 매핑하는 딕셔너리입니다.
2.  **`search_pangyo_library`**: 판교도서관 검색 및 파싱 로직 (Selenium)
3.  **`search_songpa_library`**: 송파어린이도서관 검색 및 파싱 로직 (Selenium)
4.  **`scrape_callnos_selenium`**:
    - DB에서 책 목록(`childbook_items`)을 가져옵니다.
    - 선택된 도서관의 검색 함수를 호출합니다.
    - 결과를 `book_library_info` 테이블에 **UPSERT** (없으면 추가, 있으면 갱신) 합니다.

## 4. 새로운 도서관 추가 방법

1.  `scrape_callno_from_web.py` 파일에 새로운 검색 함수(예: `search_bundang_library`)를 작성합니다.
    - 해당 도서관의 검색 페이지 URL과 DOM 구조(`CSS Selector`)를 분석하여 구현합니다.
2.  `LIBRARY_SEARCH_FUNCS` 딕셔너리에 새 도서관 이름과 함수를 등록합니다.
3.  명령어 실행 시 `--library "새도서관이름"`으로 실행합니다.

## 5. 참고 사항
- **백업**: 작업 전 `dump_childbook_items.py` 등으로 데이터를 백업하는 것을 권장합니다.
- **속도**: Selenium을 사용하므로 속도가 빠르지는 않습니다. 대량 수집 시 `limit`을 적절히 조절하여 끊어서 실행하세요.
