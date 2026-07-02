---
name: library_expansion
description: Guidelines and checklists for expanding/adding new libraries to the platform (front/back/crawler)
---

# 도서관 확장 가이드: 신규 도서관 추가 및 연동 절차

이 가이드는 '책자리' 서비스에 신규 공공도서관을 추가하여 실시간 대출 상태 조회 및 도서 청구기호 정보를 제공하는 개발 표준 절차를 안내합니다.

---

## 🎯 사용 사례

### 언제 사용하나요?
- 도서관 인프라 서비스 지역을 확장하기 위해 새로운 공공도서관을 추가할 때
- 정보나루(Data4Library) API 조회가 활성화되는 타겟 지역 도서관을 신규 연동할 때

---

## 🛠️ 단계별 구현 절차

### 1단계: 정보나루(Data4Library) 기관 코드 확인
새로운 도서관을 추가하기 전, 도서관 실시간 대출 여부를 쿼리하기 위한 **정보나루 6자리 기관 코드**를 확보해야 합니다.
1. [정보나루 도서관코드 조회 페이지](https://www.data4library.kr/libCode)에 접속합니다.
2. 도서관 이름(예: `수지도서관`)을 검색하여 `도서관코드` 열의 6자리 값을 확인합니다. (예: 수지도서관은 `111295`가 아닌 `141381` 등 고유 번호가 존재합니다.)
3. 또는 API 호출을 통해 응답 XML/JSON에서 직접 코드를 발췌합니다:
   `http://data4library.kr/api/libSrch?authKey={AUTH_KEY}&pageSize=10&pageNo=1&libName=도서관이름&format=json`

---

### 2단계: 백엔드 API 매핑 정보 등록
백엔드 서버의 실시간 대출 상태 조회 로직에 신규 도서관 이름을 바인딩합니다.
* **대상 파일**: [loan_status.py](file:///Users/1004823/Desktop/kids_library/backend/services/loan_status.py)
* **수정 내용**: `LIBRARY_CODE_MAP` 상수에 `"{도서관 명칭}": "{정보나루 코드}"` 쌍을 추가합니다.
  ```python
  LIBRARY_CODE_MAP = {
      "판교도서관": "141231",
      "송파어린이도서관": "111117",
      "반포도서관": "111295"  # 👈 추가
  }
  ```

---

### 3단계: 웹 크롤러(Selenium)에 도서관 검색/파서 구현
도서 상세 정보 조회를 돕는 청구기호 정보를 수집하기 위해, 해당 도서관의 도서 통합검색 페이지를 Selenium으로 탐색 및 파싱하는 로직을 추가합니다.
* **대상 파일**: [scrape_callno_from_web.py](file:///Users/1004823/Desktop/kids_library/backend/scripts/crawling/scrape_callno_from_web.py)
* **수정 내용**:
  1. 신규 도서관의 검색 및 파싱을 전담할 함수를 아래 구조로 구현합니다:
     ```python
     def search_banpo_library(driver, title: str, author: str, publisher: str) -> Optional[str]:
         """
         [반포도서관] 검색 및 청구기호 추출
         """
         try:
             search_url = "도서관 통합검색 주소"
             driver.get(search_url)
             
             # 1. 검색어 입력 및 실행
             WebDriverWait(driver, 10).until(
                 EC.presence_of_element_located((By.ID, "검색창_ID"))
             )
             driver.find_element(By.ID, "검색창_ID").send_keys(title)
             driver.find_element(By.CSS_SELECTOR, "검색버튼_Selector").click()
             
             time.sleep(2) # 결과 로딩 대기
             
             # 2. 결과 목록 파싱 및 해당 도서 식별
             # 3. 청구기호 영역 텍스트 추출 및 정규식 정제 후 반환
             # (예: "청구기호 : 813.8-김12ㄱ" 형태에서 "813.8-김12ㄱ" 추출)
             
             return clean_callno
         except Exception as e:
             print(f"      [반포] 검색 오류: {e}")
             return None
     ```
  2. `LIBRARY_SEARCH_FUNCS` 매핑 사전에 해당 함수를 바인딩합니다:
     ```python
     LIBRARY_SEARCH_FUNCS: Dict[str, Callable] = {
         "판교도서관": search_pangyo_library,
         "송파어린이도서관": search_songpa_library,
         "반포도서관": search_banpo_library  # 👈 추가
     }
     ```

---

### 4단계: 배치 스크래핑 실행 및 데이터 DB 적재
크롤러를 가동하여 기존 등록된 도서(`childbook_items`)들에 대한 신규 도서관 청구기호 데이터를 스크래핑한 뒤, Supabase `book_library_info` 테이블에 **UPSERT**합니다.
* **스크래핑 실행 명령어**:
  ```bash
  cd backend/scripts/crawling
  python scrape_callno_from_web.py --library "반포도서관" --limit 100
  ```
  *(💡 초기 적재 시 대량 요청으로 차단될 수 있으므로 `--limit` 파라미터로 적절히 끊어가며 적재하는 것을 권장합니다.)*

---

### 5단계: 프론트엔드 UI 상태 연동 (최종 검증 직전 노출)
데이터 수집 및 적재가 완료되면, 사용자가 화면에서 도서관을 선택할 수 있도록 목록 상수에 추가하여 UI에 노출시킵니다.
* **대상 파일**: [LibraryContext.tsx](file:///Users/1004823/Desktop/kids_library/frontend/context/LibraryContext.tsx)
* **수정 내용**: `AVAILABLE_LIBRARIES` 배열 상수에 신규 도서관 이름을 추가합니다.
  ```typescript
  const AVAILABLE_LIBRARIES = ['판교도서관', '송파어린이도서관', '반포도서관'] as const  // 👈 추가
  ```

---

## 🚦 기능 검증 (QA Checklist)

도서관 설정 추가 후, 로컬 개발 환경(`npm run dev` / `uvicorn main:app --reload`)에서 다음의 기능이 정상적으로 구현되었는지 QA를 수행합니다.

- [ ] **마이페이지 변경 테스트**: 마이페이지의 '내 도서관 설정'에서 새로 추가한 도서관으로의 변경 및 저장이 즉시 반영되는가?
- [ ] **도서 목록 청구기호 정합성**: 목록 화면에서 해당 도서관으로 선택되었을 때, 다른 도서관의 청구기호가 겹치지 않고 해당 도서관의 청구기호 정보만 깔끔하게 노출되는가?
- [ ] **실시간 대출 API 연동**: 도서 상세 진입 시 정보나루 API를 정상 호출하여 `'대출가능'`, `'대출중'` 배지 및 소장 상태가 정상 마운트되는가? (만약 미소장 혹은 데이터 미존재 시 `'미소장'` 배지가 회색 톤으로 올바르게 노출되는가?)

---

## ⚠️ API 통신 및 동적 적재 트러블슈팅 가이드

1. **정보나루 일일 500건 한도 초과 (outOflimit) 대응**:
   - 정보나루 API는 사용 공인 IP가 미등록된 상태일 경우 일일 500회 호출로 제한되어 수집 중 차단됩니다.
   - 대량 벌크 수집(1,000건 이상) 전에 반드시 [도서관 정보나루 웹사이트] 마이페이지에서 **수집을 구동할 서버 또는 로컬 장비의 공인 외부 IP를 등록**해야 합니다. (등록 시 20만 건으로 한도 증대)
2. **asyncio 다른 이벤트 루프 바인딩 오류 (RuntimeError) 방지**:
   - `SEMAPHORE = asyncio.Semaphore(5)`와 같이 전역 범위에서 세마포어를 생성하면 `asyncio.run` 시 루프 바인딩 에러가 터집니다.
   - 세마포어는 반드시 비동기 실행 스레드 내부에서 지연 로딩(`get_semaphore()`) 함수 형태로 구성하여 생성 및 리턴되도록 설계해야 합니다.

---

## 📖 도서 청구기호 수집 파이프라인 개발 표준 (Lesson Learn)

신규 도서관 추가 및 기존 도서의 청구기호 배치 수집기(Batch Ingestor)를 구현할 때는 다음의 핵심 아키텍처 규칙을 엄격히 고수한다.

1. **ISBN 13자리 전적 신뢰 원칙 (제목 유사도 검사 배제)**:
   - 아동 도서는 "곰", "숲" 등 1~2글자로 이루어진 짧은 제목이 많아 제목 부분 일치 검증 시 오매칭 및 데이터 오염률이 비정상적으로 치솟는다.
   - 따라서 도서 검색 결과 정합성 검증은 오직 **ISBN 13자리 1:1 완벽 일치 여부**만 검사하고, 제목 매칭 로직은 배제한다.
2. **DB UNIQUE 제약 및 외래키(FK) 안전 우회 진단**:
   - `book_library_info`에 중복 데이터 누적을 막는 복합 UNIQUE 인덱스가 작동하는지 검증하기 위한 upsert 테스트 수행 시, 가상 ID(예: `-1`)를 하드코딩해 주입하면 외래키 제약조건(`childbook_items_fkey`)을 위반해 전체 트랜잭션이 깨진다.
   - 반드시 `childbook_items`에서 **실제 존재하는 도서 ID 1개를 사전 쿼리**하여 upsert 테스트에 사용하고, 검증 직후 해당 테스트 레코드를 명시적으로 delete하여 지워주도록 설계한다.
3. **체크포인트 기반 멱등성 설계 (Resume Flag)**:
   - 대량 배치 스크립트 작성 시 API 한도 초과 또는 일시적 네트워크 타임아웃에 완벽히 대응할 수 있도록, 처리 중인 도서관명과 `last_book_id`를 임시 JSON 파일(`.populate_checkpoint.json` 등)로 백업하는 기능을 구현한다.
   - 스크립트 재실행 시 `--resume` 플래그를 제공하여 마지막 중단 지점부터 낭비 없이 이어받기를 지원한다.
4. **하이브리드 수집 파이프라인 워크플로우**:
   - **1단계**: 정보나루 API 기반 벌크 적재 (속도가 빠르고 부하가 적음).
   - **2단계**: API 상에서 미소장(Null)으로 식별된 도서들만 콕 집어, 대상 도서관 웹 검색페이지로 Selenium 크롤링 폴백 구동하여 90% 이상의 커버리지를 완비한다.
