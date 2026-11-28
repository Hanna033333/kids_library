# 공통 영역 및 기타 정적 페이지

> 대상: 전역 레이아웃(`layout.tsx`), 공통 컴포넌트, `/c/[tag]`, `/intro`, `/terms`, `/privacy`, `/marketing`, `404`

---

## 1. 현재 구현된 기능 (As-Is)

### 1-1. 전역 레이아웃 및 트래킹 (`app/layout.tsx`, `providers.tsx`)
- **Provider 중첩**: `AuthProvider` > `QueryClientProvider` > `LibraryProvider`
- **전역 마운트 컴포넌트**: `HistoryTracker`, `SignupWelcomeModal`
- **GA4 (`G-FG2WYB82L9`)**: 봇/헤드리스 브라우저 및 `?ignore=true`(localStorage 영구 저장) 접근 시 트래킹 자동 차단
- **뷰포트/성능**: `userScalable=false`, 알라딘 이미지 CDN(`image.aladin.co.kr`) preconnect/dns-prefetch

### 1-2. 공통 헤더 & 스마트 뒤로가기 (`PageHeader`, `BackButton`, `HistoryTracker`)
- **PageHeader**: `sticky top-0` 3분할 (`좌 w-[84px]` / `중앙 flex-1 truncate text-lg` / `우 w-[84px]`)
  - 좌측 기본: 뒤로가기(`<`) 버튼 + `showHome=true`일 때 홈(`Home`) 버튼
- **스마트 뒤로가기**: `HistoryTracker`가 `sessionStorage['checkjari_history']`에 내부 이동 경로 기록
  - 외부 유입/직접 진입 등 내부 히스토리가 없으면 뒤로가기 1회로 홈(`/`)으로 이동

### 1-3. 공통 푸터 (`Footer`)
- 저작권(`© 2026 책자리. All rights reserved.`)
- 링크: `서비스 소개`(`/intro`) | `이용약관`(`/terms`) | `개인정보 처리방침`(`/privacy`) | `고객 문의`(`mailto:contact@chaekjari.com`)

### 1-4. 도서관 선택기 (`LibrarySelector`)
- **트리거**: 기본 버튼(선택 도서관명 15자 말줄임 또는 `'도서관을 선택해주세요'`) 또는 커스텀 트리거
- **바텀시트/모달**: 모바일 바텀시트 / 데스크톱 중앙 모달
  - `availableLibraries` 목록 선택 시 `setSelectedLibrary` 반영 + GA `select_library`
  - 하단 `"우리 동네 도서관이 아직 없나요? 도서관 신청하기"` 외부 구글 폼 새 창 링크

### 1-5. 로그인 유도 & 가입 온보딩 모달
- **LoginPromptModal**: 비로그인 상태에서 찜하기·도서관 확인 등 클릭 시 노출
  - 카카오 / Google OAuth 시작 (`returnUrl` 자동 저장, 뒤로가기 복귀 시 로딩 해제)
- **SignupWelcomeModal**: 가입 직후(`sessionStorage.showSignupComplete === 'true'`) 전역 노출
  - **닉네임(필수)**: 2~10자 한글/영문/숫자, 공백 자동 제거, 300ms 디바운스 중복 검사
  - **우리 아이 연령대(선택)**: `0~3세`, `4~7세`, `8~12세`, `13세 이상` 토글
  - **자주 가는 도서관(선택)**: 드롭다운(기본값 서울시립어린이도서관, `'나중에 선택할게요'` 포함)
  - 저장 시 `PATCH /api/auth/me` 반영 + GA `complete_onboarding`
- **ProfileDropdown**: 로그인 시 아바타 버튼 노출, 클릭 시 `/my-page` 직행 (실제 드롭다운 아님)

### 1-6. 검색바 (`SearchBar`)
- `sticky top-0`, 하단 3px 앰버 보더 인풋 + 입력값 있을 때 `X` 지우기 버튼 + 검색 아이콘 제출 버튼
- 입력 후 **600ms 디바운스** 자동 검색 (단, 자음/모음 단독 입력 중에는 보류)

### 1-7. 단축 링크 리다이렉트 (`/c/[tag]`)
- 스레드 댓글 유입용 단축 경로 (`app/c/[tag]/route.ts`)
- 학년 패턴(`초등N학년`, `gradeN`) → `/books?curation=교과서수록&tag=초등N학년&utm_source=threads...`
- 일반 테마/태그 → `/collections/curation/{slug}?utm_source=threads...`

### 1-8. 기타 정적/안내 페이지
- **서비스 소개 (`/intro`)**: Hero → 메인 비주얼 → 문제/해결 → 주요 기능 2단 → `"책자리 시작하기"`(`/`) CTA
- **약관 3종**: `/terms`(이용약관), `/privacy`(개인정보 처리방침), `/marketing`(마케팅 수신 안내) — 모두 `PageHeader` + 정적 본문
- **404 (`not-found.tsx`)**: 안내 문구 + `"홈으로 돌아가기"` + 현재 경로 표시 + GA `page_not_found`

---

## 2. 수정/추가 요청 (Draft)

<!-- 여기에 수정하거나 새로 추가하고 싶은 공통 기능을 편하게 적어주세요 -->
- [ ]

---

## 3. 정책 / 주의사항
- 내부 문서(`/intro`, `/terms`, `/privacy`)는 새 창 대신 내부 라우트 전환 우선.
- 외부 링크(노션 공지, 도서관 신청 구글 폼, 교보문고 등)만 새 창(`_blank`) 허용.
- 헤더 타이틀은 모바일 360px 말줄임 방지를 위해 공백 포함 최대 11자 이내 유지.
