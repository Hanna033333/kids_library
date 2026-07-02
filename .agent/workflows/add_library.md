---
description: 신규 도서관을 서비스에 등록하고, 크롤링 및 백엔드/프론트엔드 연동을 진행하는 워크플로우
---

# 🗺️ /add_library 도서관 추가 워크플로우

이 워크플로우는 사용자가 `/add_library` 단축어를 입력했을 때 실행되며, 서비스에 새로운 도서관을 등록하고 설정하는 작업을 순서대로 가이드하고 처리합니다.

---

## 📌 실행 절차

에이전트는 `/add_library`가 호출되면 다음 5단계 절차를 수행하여 사용자에게 가이드하고 코드를 작성/수정해야 합니다.

### 1단계: 도서관 정보 확인
- 사용자에게 추가할 **도서관 명칭**을 확인합니다.
- 해당 도서관의 **정보나루 6자리 기관 코드**가 확보되었는지 확인합니다.
  - 만약 코드가 없다면 정보나루 API를 조회하여 코드 후보를 제시하고 사용자의 확인을 받습니다.

### 2단계: 백엔드 매핑 업데이트
- [loan_status.py](file:///Users/1004823/Desktop/kids_library/backend/services/loan_status.py)의 `LIBRARY_CODE_MAP` 딕셔너리에 새 도서관명과 정보나루 코드를 추가합니다.

### 3단계: 크롤러 검색/파서 함수 추가
- [scrape_callno_from_web.py](file:///Users/1004823/Desktop/kids_library/backend/scripts/crawling/scrape_callno_from_web.py)에 신규 도서관의 Selenium 스크래핑 검색 함수(`search_xxx_library`)를 작성합니다.
  - 해당 도서관 웹페이지의 검색 Input ID 및 검색 버튼 Selector, 그리고 결과 영역에서 청구기호를 발췌하는 정규식 로직을 적용합니다.
  - `LIBRARY_SEARCH_FUNCS` 매핑 딕셔너리에 함수를 등록합니다.

### 4단계: 데이터 스크래핑 실행
- 데이터베이스 적재 명령어를 사용자에게 제안하여 실행 승인을 얻고 크롤러를 가동합니다.
  - 명령어 예시: `python scrape_callno_from_web.py --library "{도서관이름}" --limit 100`

### 5단계: 프론트엔드 UI 목록 업데이트 (최종 노출)
- 데이터 수집 및 적재가 정상적으로 완료되면, [LibraryContext.tsx](file:///Users/1004823/Desktop/kids_library/frontend/context/LibraryContext.tsx)의 `AVAILABLE_LIBRARIES` 상수 배열에 신규 도서관 명칭을 추가하여 UI에 노출되도록 반영합니다.

### 6단계: 화면 검증 안내 (QA)
- 변경된 프론트엔드 로컬 서버 환경에서 마이페이지 ➡️ 도서 목록/상세 ➡️ 실시간 대출 상태 배지가 에러 없이 올바르게 출력되는지 사용자가 최종 수동 QA를 수행하도록 안내합니다.
