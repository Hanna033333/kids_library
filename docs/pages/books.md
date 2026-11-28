# 도서 목록 / 검색 / 컬렉션 (`/books`, `/collections/*`, `/caldecott`)

> 파일: `app/books/page.tsx`, `components/BooksPageClient.tsx`, `components/BookList.tsx`, `components/BookItem.tsx`, `components/FilterBar.tsx`, `components/IntegratedFilterModal.tsx`, `app/collections/**/*`, `app/caldecott/*`

---

## 1. 현재 구현된 기능 (As-Is)

### 1-1. 도서 검색 및 큐레이션 목록 (`/books`)
- **렌더링**: `force-dynamic` SSR + 클라이언트 `BooksPageClient`
- **지원 URL 쿼리**: `q`(검색어), `curation`(큐레이션 태그/슬러그), `age`(`0-3`/`4-7`/`8-12`/`13+`), `tag`(학년 `초등N학년`), `sort`(`title`/`callno`/`confidence_score_desc`), `author`(작가명)
- **상단 → 하단 UI**:
  1. `PageHeader`: 동적 타이틀(`작가명` / `교과서 수록도서` / 특수·AI 큐레이션명 / 연령별 / `도서 검색`), `showHome=true`, 우측 검색 토글 아이콘 + 프로필 아바타
  2. `SearchBar`: `q`가 있거나 필터가 없을 때 기본 노출, 그 외에는 헤더 검색 아이콘으로 토글
  3. **상단 통합 1줄 툴바 (`FilterBar` + 공유 아이콘 | 우측 도서관 칩)** (비로그인 전면 개방):
     - 좌측: `필터` 버튼(검색/작가 목록 한정) + **연령/학년 드롭다운 칩**(`연령 ▾` / `학년 ▾`, 탭 시 바텀시트로 선택, 0권 연령은 `도서 없음` 비활성) + **공유 버튼**(`Share2`, `curation` 목록 한정, 연령 칩과 동일한 흰색 원형 테두리 버튼)
     - 우측: **도서관 칩** — 미설정 시 `📍 내 도서관 설정 ▾`, 설정 완료 시 `📍 {도서관명} ▾` → 탭 시 로그인 없이 전국 도서관 `LibrarySelector` 바텀시트 즉시 오픈 (검색 대기 상태에서는 도서관 설정 시 인기 추천 도서 헤더 영역에 노출)
  4. **도서 그리드 (`BookList`, 페이지당 24권, 2/3/4열)**:
     - 각 카드(`BookItem`): 표지 + 좌상단 학년/연령 배지 + 우상단 찜 하트 + 제목 + 큐레이션 태그 최대 2개 + 실시간 대출 배지(도서관 설정 시 비로그인 포함 전면 노출, 청구기호 텍스트는 미노출)
     - **홈 시각적 연속성**: 검색어가 없는 큐레이션/연령 목록은 홈 노출 상위 도서(7~8권)를 최상단에 우선 고정
     - **모바일 무한 스크롤**: `window.innerWidth < 768`에서 `IntersectionObserver`로 다음 페이지 자동 로드 *(참고: 데스크톱에는 별도 페이지네이션 버튼 미노출)*
- **상태별 화면**:
  - **검색 대기 상태** (검색어·필터 모두 없음): `"인기 추천 도서"` 8권 카드 박스
  - **결과 0건 (Empty State)**: 상단 알림 바 + 폴백 추천 도서 최대 8권 (현재 큐레이션 전체 연령 → 현재 연령 인기 → 전체 인기 순)
  - **소수 결과 보강**: 큐레이션 + 연령 조합이 1~6권일 때 하단에 `"다른 연령대의 책은 어떨까요?"` 최대 8권 추가 노출
- **선호 연령 자동 적용**: 로그인 유저가 URL에 `age` 없이 진입 시 `preferredChildAge` 자동 적용 (단, 해당 큐레이션에 0권이면 전체 연령 유지 + 토스트 안내)
- **통합 필터 모달 (`IntegratedFilterModal`)**: 연령/학년 선택 + 정렬(`청구기호순` / `제목순`) + 초기화/적용 버튼

### 1-2. 큐레이션 테마 허브 (`/collections`)
- **렌더링**: ISR (`revalidate = 3600`)
- **UI**: `PageHeader("큐레이션 테마")` → 스티키 상황 처방 탭 바(`SITUATION_PRESCRIPTIONS`) → 선택 처방 요약 배너 → 2~3열 매거진 포스터 카드 그리드(클릭 시 `/collections/curation/{slug}`) → `Footer`

### 1-3. 큐레이션 SEO 랜딩 (`/collections/curation/[tag]`)
- **렌더링**: SSG + ISR (`revalidate = 3600`), 전체 `VALID_TAXONOMY` + 특수 큐레이션 6종 정적 생성
- **UI/동작**: `BooksPageClient`를 그대로 사용하므로 `/books`와 UI·필터·공유·대출·찜 기능이 100% 동일

### 1-4. 연령별 컬렉션 (`/collections/age/[age]`)
- **허용 경로**: `0-3`, `4-7`, `8-12`, `teen` (그 외 404), SSR
- **UI**: `PageHeader("{연령} 추천 도서")` → `SearchBar`(상시 노출) → `FilterBar`(`필터` 버튼 항상 노출, 공유 버튼 없음) → `BookList`
- 연령 칩 클릭 시 `/collections/age/{age}`로 라우트 이동

### 1-5. 어린이도서연구회 (`/collections/research-council`)
- **렌더링**: `force-dynamic`, `PageHeader("어린이도서연구회")` → `SearchBar`(상시 노출) → `FilterBar` → `BookList`
- 로그인 유저의 `preferredChildAge` 자동 적용

### 1-6. 칼데콧 수상작 전용 (`/caldecott`)
- **렌더링**: SSR 전체 일괄 조회
- **UI**: `PageHeader("칼데콧 수상작")` → 총 권수 안내 → 도서 그리드(`BookItem`, 찜/대출 배지 미노출) → 하단 `"칼데콧 메달이란?"` 안내 카드
- 필터·검색·정렬·페이지네이션 없음

---

## 2. 수정/추가 요청 (Draft)

<!-- 여기에 도서 목록/검색/컬렉션 페이지에 수정하거나 추가하고 싶은 기능을 편하게 적어주세요 -->
- [ ]

---

## 3. 정책 / 주의사항
- 전국 1,600+ 공공도서관 실시간 대출 조회는 비로그인 유저에게도 전면 개방됨 (도서관 선택 시 목록 카드에 대출 가능 배지 노출).
- 결과 0건 시 이탈 방지를 위해 반드시 폴백 추천 도서 섹션 유지.
- **참고(현재 코드 특이사항)**: `BookList`의 무한 스크롤이 모바일(`width < 768`)에서만 동작하여, 데스크톱 24권 초과 목록의 페이지네이션/더보기 방식 검토 필요.
