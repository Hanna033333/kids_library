# 로그인 / 회원가입 (`/auth`, `/auth/callback`)

> 파일: `app/auth/page.tsx`, `app/auth/AuthClient.tsx`, `app/auth/signup/page.tsx`, `app/auth/callback/page.tsx`, `app/auth/login/page.tsx`, `app/login/page.tsx`, `app/signup/page.tsx`

---

## 1. 현재 구현된 기능 (As-Is)

### 1-1. 라우트 정리
- `/auth`, `/auth/signup`: 동일 로그인/가입 화면(`AuthClient`) 렌더링 (`force-dynamic`, `noindex`)
- `/auth/login`, `/login` → `/auth` 리다이렉트
- `/signup` → `/auth/signup` 리다이렉트
- `/auth/callback`: OAuth 콜백 후처리 전용 (처리 중 `PageLoader`만 표시)

### 1-2. 로그인 / 가입 화면 (`AuthClient`)
- **UI**: 좌상단 `BackButton`, 로고, USP 문구, 조건부 에러 박스, **카카오로 로그인** 버튼, **Google로 로그인** 버튼, 약관 동의 안내(`/terms`, `/privacy` 링크)
- **OAuth 전용**: 이메일/비밀번호 입력 폼 없음
- **마지막 로그인 표시**: `localStorage('last_login_provider')` 일치 버튼에 `"마지막 로그인"` 뱃지 노출
- **QA 버튼**: 개발/Preview(비운영) 환경에서만 `"QA 테스터로 로그인 (개발용)"` 버튼 노출
- **자동/예외 처리**:
  - 이미 로그인 상태면 `sessionStorage('returnUrl')` 또는 `/`로 즉시 이동
  - `?provider=kakao|google` 진입 시 해당 OAuth 1회 자동 실행
  - 외부 OAuth 화면에서 뒤로가기/BFCache 복귀 시 로딩 해제 및 `returnUrl` 복귀
  - 에러 쿼리 안내: `existing_account`(이메일 중복), `auth_failed`(처리 오류), `email_required`(이메일 미제공)

### 1-3. OAuth 콜백 후처리 (`/auth/callback`)
1. 세션 확인 (실패 시 에러 쿼리와 함께 로그인 화면 리다이렉트)
2. **이메일 미제공 차단**: 이메일이 없으면 강제 `signOut()` 후 `/auth?error=email_required` 이동
3. **신규/미완료 프로필 자동 등록**: `members`에 없거나 닉네임이 없으면 랜덤 닉네임으로 `POST /api/auth/me/agreements` 호출 (약관/개인정보 동의 `true`, 마케팅 `false`, 409 시 새 랜덤 닉네임으로 1회 재시도)
4. **가입 축하 온보딩 플래그**: 생성 5분 이내 신규 계정이고 미노출 상태면 `sessionStorage`에 `showSignupComplete` 설정 (홈/복귀 페이지에서 `SignupWelcomeModal` 오픈)
5. `sessionStorage('returnUrl')` 또는 `/`로 `window.location.replace` 이동

---

## 2. 수정/추가 요청 (Draft)

<!-- 여기에 로그인/회원가입 흐름에 수정하거나 추가하고 싶은 기능을 편하게 적어주세요 -->
- [ ]

---

## 3. 정책 / 주의사항
- 로그인/가입 페이지는 검색엔진 색인 제외(`robots: noindex, nofollow`).
- 이메일 미제공 카카오 계정은 가입 차단 처리 유지.
