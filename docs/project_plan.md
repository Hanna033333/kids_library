# 책자리 – 제품 요구사항 정의서 (PRD / 작업계획서)

> **기준 시점**: 2026년 11월 26일 상용(`main`) 배포 기준 현행화  
> **[피봇 기록 - 2026.05]** 서비스 핵심 가치를 "청구기호 기반 판교 로컬 유틸리티"에서 "전국 학부모 대상 정서·상황별 큐레이션 플랫폼"으로 전환. 이후 전국 다중 도서관(13개) 실시간 대출 연동, 아이 선호 연령대 맞춤 정렬, 부모 리뷰·공감 뱃지, 내지 미리보기, Threads 자동 발행 파이프라인까지 상용 반영 완료.

---

## 0. 프로젝트 한 줄 요약
책자리는 **어떤 책을 읽혀야 할지 모르는 부모를 위한, 상황별·정서별 맞춤 어린이 도서 큐레이션 서비스**다.  
발견한 책은 **내 주변 도서관(전국 13개 지원)의 실시간 대출 가능 여부 및 청구기호 확인**과 **교보문고 구매**까지 바로 연결된다.

---

## 1. 현재 단계의 목표 및 KPI
- **전국 단위 DAU 100명** 달성 및 큐레이션 중심 탐색 경험 고도화
- `홈 큐레이션 / 검색 유입 → 도서 상세(리뷰·미리보기·추천) → 도서관 대출 확인 or 교보 구매` 전환 흐름 최적화
- 아이 연령·선호 도서관 기반 개인화 및 바이럴 공유 루프 강화

### 성공 기준 (KPI)
- **[NSM] 도서 상세 페이지 DAU** (일별 유니크 도달자 수) — 홈/리스트/네이버·구글 검색/Threads 등 모든 유입 경로 포괄
- **[보조: 액션 전환] 행동 전환 수**: 교보 구매 클릭 + 도서관 대출 확인 클릭 합산
- **[보조: 인게이지먼트] 회원 가입 수, 내 책장 찜하기 수, 부모 리뷰 작성 수**
- **[리텐션] 7일 재방문율 35% 이상** (주간 큐레이션 갱신 주기 기반 재방문)
- 모바일 우선(Mobile-First, 360px 기준) 완전 사용 가능

---

## 2. 핵심 가치 제안 (Value Proposition)

### 메인 소구점: "Curation First + The Ultimate Conversion"
> **"어떤 책을 읽혀야 할지 모르는 부모를 위한 상황별 정서 맞춤 큐레이션 + 내 주변 도서관 3초 대출 조회"**

- **Curation First (발견)**: 아이의 연령(`0~3세`, `4~7세`, `8~12세`, `13세 이상`)뿐 아니라 정서·발달 상황(잠자리, 감정조절, 사회성, 교과서 수록 등 72개 테마)에 맞춘 큐레이션을 첫 화면에 제공
- **Social Proof (확신)**: 알라딘 연동 내지 미리보기·글밥 정보와 부모 별점·범용 10종 공감 뱃지·한줄평으로 책 선택의 확신 제공
- **The Ultimate Conversion (행동 연결)**: 발견한 책을 내 선호 도서관에서 바로 대출 가능한지 실시간 확인하거나, 미소장·즉시 구매 희망 시 교보문고로 원클릭 연결

---

## 3. 현재 상용 배포 범위 (Scope)

### 포함 (상용 운영 중)

#### 3-1. 홈 화면 큐레이션 (`/`)
- **에디터 스포트라이트 배너 (`SpotlightBanner`)**: 주요 시즌/테마 프로모션 롤링 캐러셀
- **AI 주간 큐레이션 서가**: `weekly_schedule.json` 기반 7일 주기 자동 로테이션 (스케줄 만료 시 프론트/백엔드 동기화 LCG 폴백 적용)
- **50+ 전문 테마 큐레이션 쇼케이스 (`ThemeCurationShowcase`)**: 상황별 처방전 기반 테마 미리보기 및 전체 모음 페이지(`/collections`) 연결 (총 72개 테마 태그 운영)
- **2022 개정 교과서 수록도서 쇼케이스 (`TextbookCurationShowcase`)**: 초등 1~6학년 가로 스크롤 탭 제공
- **전문·특별 큐레이션**: 칼데콧 수상작(`/caldecott`), 어린이도서연구회 추천(`/collections/research-council`), 시즌별 방학 추천도서(기간 조건부 활성화)
- **아이 연령 맞춤 우선 정렬**: 로그인 회원이 마이페이지에서 `preferred_child_age`를 설정한 경우, 홈 큐레이션 서가 도서를 해당 연령대 우선으로 클라이언트 재정렬
- **표지 이미지 검증 필터**: 표지 이미지가 없거나 플레이스홀더(`noimg`)인 도서는 홈 화면 노출 차단
- **서비스 공지사항**: 하단 공지 배너(`latest_notice.json` ↔ Notion 공지 페이지 연동)

#### 3-2. 검색, 필터링 및 도서 목록 (`/books`, `/collections/*`, `/c/[tag]`)
- **검색**: 제목, 저자, 키워드 기반 통합 검색 및 저자별 필터링
- **필터링**:
  - 표준 연령대 필터 (`0-3`, `4-7`, `8-12`, `13+`), 큐레이션 내 도서 0권인 연령 칩 자동 비활성화
  - 카테고리 필터 및 세부 학년 태그 필터(`초등1학년`~`초등6학년`)
  - 큐레이션별 필터 및 단축 리다이렉트 URL(`/c/[tag]`) 지원
- **정렬**:
  - AI 큐레이션: AI 신뢰도순(`confidence_score_desc`) 기본
  - 일반 검색 및 특수 큐레이션(칼데콧·교과서·연구회 등): 제목 오름차순(`title`) 기본
  - 인기순(`popular`), 선택 도서관 청구기호순(`callno`) 지원
- **Empty State 폴백 추천**: 검색/연령 필터 조합 결과가 0건일 때 이탈 방지를 위한 폴백 추천 도서 섹션 자동 노출
- **도서관 소장/대출 표시 정책**:
  - 로그인 + 선호 도서관 설정 유저에게만 목록 카드(`BookItem`) 내 청구기호 및 실시간 대출 가능 배지를 2단 배치로 노출
  - 비로그인/도서관 미설정 유저에게는 도서관 대출 확인 유도 배너 노출
- **무한 스크롤 & 큐레이션 공유**: 24권 단위 점진적 로딩, 큐레이션 헤더 공유 버튼(URL 복사/SNS 공유)

#### 3-3. 도서 상세 (`/book/[id]`)
- **도서 기본 정보 및 미리보기**:
  - 제목, 저자, 출판사, ISBN, 알라딘 연동 도서 소개
  - 페이지 수, 글밥 수준(`text_level`), **내지 미리보기 모달(`BookPreviewModal`)**
  - 표준 태그 최대 4개 노출: `[메타 태그 1개(구체적 학년 우선, 없으면 연령)]` + `[핵심 큐레이션 태그 최대 3개]`
- **전국 13개 공공도서관 연동 (`LibrarySelector`)**:
  - 바텀시트 도서관 선택기 제공
  - 선택 도서관의 청구기호·권 정보(`vol`) 및 Data4Library 기반 실시간 대출 가능 여부 표시
  - 미소장 또는 API 지연 시 graceful fallback 표시 및 교보문고 구매 CTA 병행
- **구매 & 공유 & 오류 신고**:
  - 교보문고 구매 링크 (LinkPrice Deep Link)
  - 도서 상세 공유 버튼 및 청구기호/도서 정보 오류 신고 (구글 폼)
- **부모 평점 & 공감 뱃지 리뷰 (`BookReviewSection`)**:
  - 별점(1~5점) + 범용 10종 공감 뱃지(도서 특징 5종 / 아이 반응 5종) + 한줄평
  - 로그인 회원 대상 **1인 1도서 1리뷰** 작성·수정·삭제 지원 (비로그인 시 조회 가능, 작성 시 로그인 유도)
  - 내부 관리용 플래그(`is_ai_generated`)는 UI에 비노출
- **4단계 큐레이션 추천 영역**:
  1. 대표/교과서 큐레이션 추천 리스트 (7권)
  2. 또래 연령별 추천 리스트 (7권)
  3. AI 순수 주제 큐레이션 추천 리스트 (7권, 대표 큐레이션과 주제 상이 시)
  4. 동일 작가 추천 리스트 (DB 내 동일 작가 도서 존재 시)

#### 3-4. 회원 시스템, 마이페이지 & 내 책장 (`/auth/*`, `/my-page`, `/my-library`)
- **소셜 로그인**: 카카오, 구글 OAuth (Supabase Auth)
- **프로필 및 개인화 (`/my-page`)**:
  - 가입 시 자동 닉네임 생성, 중복 확인 후 닉네임 변경 가능
  - **우리 아이 선호 연령대(`0-3`, `4-7`, `8-12`, `13+`)** 설정 (DB 동기화 → 홈 큐레이션 맞춤 정렬 반영)
  - **선호 도서관** 설정 (13개 도서관 중 선택)
  - 내가 작성한 리뷰 목록 조회, 약관/마케팅 수신 동의 관리, 회원 탈퇴(사유 수집 포함)
- **내 책장 (`/my-library`)**:
  - 찜(위시리스트) 저장 도서 관리 (로그인 회원 DB 기반, 비로그인 시 로그인 유도 모달)
  - 선택된 선호 도서관 기준 저장 도서 전체의 실시간 대출 가능 여부 일괄 조회 및 **대출 가능 권수 요약** 제공
  - 내 책장 공유 기능

#### 3-5. 마케팅·콘텐츠 자동화 및 SEO
- **Threads 주간 자동 발행 파이프라인**:
  - 주간 큐레이션 도서 기반 1080x1080 카드뉴스(Pillow) 및 캡션(Gemini) 자동 생성
  - 텔레그램 봇 미리보기 및 원클릭 승인 워크플로우 → 정규 스케줄 자동 발행 및 첫 댓글 랜딩 링크 등록
- **SEO & 분석**:
  - 동적 `sitemap.ts`, 페이지별 Open Graph / Twitter 메타데이터, JSON-LD(`WebSite`, `Organization`)
  - GA4 이벤트 추적 (`dataLayer` 표준 큐잉, 회원가입/검색/도서상세/대출확인/구매클릭/도서관선택/공유 등)

### 제외 (현재 미포함)
- 자체 도서 결제 및 배송
- 도서관 직접 대출 예약/연장 (각 도서관 사이트/오프라인 방문 연결)

---

## 4. 핵심 사용자 흐름

### Flow A. 전국 유저 (발견 → 확신 → 구매/대출)
1. 보호자가 검색엔진/Threads/홈 화면을 통해 상황·연령에 맞는 큐레이션 서가에 진입한다.
2. 관심 도서를 클릭해 상세 페이지에서 **내지 미리보기, 글밥 수준, 부모 공감 뱃지·한줄평**을 확인한다.
3. 교보문고에서 바로 구매하거나, 선호 도서관을 선택해 소장/대출 가능 여부를 확인한다.
4. 하단 4단계 추천 영역(교과서/또래/주제/동일 작가)을 통해 연관 도서를 연속 탐색한다.

### Flow B. 도서관 이용 회원 (개인화 → 책장 관리 → 방문)
1. 소셜 로그인 후 마이페이지에서 **우리 아이 연령대**와 **자주 가는 도서관**을 설정한다.
2. 홈/목록에서 아이 연령에 맞춘 큐레이션을 탐색하며 마음에 드는 책을 **내 책장(찜)**에 담는다.
3. 도서관 방문 전 `/my-library`에서 찜한 책들의 **실시간 대출 가능 여부와 청구기호**를 한눈에 확인한다.
4. 도서관에서 청구기호로 책을 찾고, 정보가 다른 경우 오류 신고를 제출한다.

---

## 5. 운영 원칙
- **큐레이션 콘텐츠 품질 최우선**: 7-Book Rule(모든 큐레이션 테마 최소 7권 이상 확보) 및 첫 번째 태그 정밀 매칭 유지
- **발견 → 행동 최단 경로 유지**: 불필요한 단계를 줄이고 3단계(진입 → 발견 → 대출/구매 확인) 내 핵심 가치 완결
- **불완전한 데이터의 투명한 처리**: 미소장/API 점검 시 에러 대신 명확한 상태 표시 및 교보문고 구매 폴백 제공
- **모바일 우선(Mobile-First)**: 360px 뷰포트 기준 단일 컬럼, 최소 48px 터치 타겟, 한 손 조작성 보장

---

## 6. 기술 스택 및 외부 연동

### Frontend
- **Next.js** (App Router, SSR/ISR)
- **TypeScript**, **Tailwind CSS**
- **TanStack React Query** (클라이언트 데이터 페칭 및 캐싱)
- **Hosting**: Vercel (`main` → Production, `dev` → Preview)

### Backend
- **FastAPI** (Python, 비동기 백그라운드 스케줄러 포함)
- **Supabase** (PostgreSQL, Auth OAuth, RLS 보안 정책, Storage)
- **Hosting**: AWS Lightsail (`./deploy_to_aws.sh` 실행 시 서버 동기화 및 `fastapi.service` 재시작)

### External APIs & Integrations
- **Data4Library (정보나루) API**: 도서관별 소장 여부 및 실시간 대출 가능 상태 조회 (`bookExist`)
- **알라딘 Open API**: 도서 표지, 줄거리, 페이지 수, 글밥 수준, 내지 미리보기 URL 연동
- **LinkPrice Deep Link**: 교보문고 도서 구매 제휴 연결
- **Google Gemini API**: AI 도서 태그 분류 및 Threads 카드뉴스/캡션 생성
- **Threads Graph API & Telegram Bot API**: 주간 큐레이션 콘텐츠 미리보기·승인·자동 발행
- **Google Analytics 4 (GA4)**: 퍼널 및 이벤트 트래킹

---

## 7. API 설계 (상용 기준)

### 7-1. Base URL
- **Production**: `https://api.checkjari.com`
- **Development**: `http://127.0.0.1:8000`
- **API Prefix**: `/api` (`NEXT_PUBLIC_API_URL`)

### 7-2. 도서 검색·조회 (`/api/books`)
- `GET /api/books/search`: 통합 검색 및 필터링
  - Query: `q`, `age` (`0-3`, `4-7`, `8-12`, `13+`), `category`, `curation`, `tag` (예: `초등1학년`), `library`, `sort` (`title` | `callno` | `confidence_score_desc` | `popular`), `page`, `limit` (기본 20, 최대 100), `include_library_info`
- `GET /api/books/list`: 전체 도서 목록 조회 (페이지네이션, 필터/정렬 파라미터 동일)
- `GET /api/books/{book_id}`: 도서 상세 정보 조회 (기본 정보, `book_library_info`, 알라딘 정보, 찜 횟수)
- `POST /api/books/by-ids`: 다건 도서 ID 기반 상세 일괄 조회
- `POST /api/books/loan-status`: 선택 도서관 기준 다건 도서(최대 50권) 실시간 대출 상태 병렬 조회
  - Body: `{ "book_ids": [1, 2, 3], "library_name": "판교도서관" }`
  - `book_library_info`에 청구기호가 없는 도서는 외부 API 호출 없이 즉시 `미소장` 응답

### 7-3. 부모 리뷰 & 공감 뱃지 (`/api/books`)
- `GET /api/books/{book_id}/reviews`: 도서별 리뷰 목록, 평균 별점, 뱃지 집계 조회
- `POST /api/books/{book_id}/reviews`: 리뷰 작성 (인증 필수, 1인 1도서 1리뷰)
- `PATCH /api/books/{book_id}/reviews/{review_id}`: 본인 리뷰 수정
- `DELETE /api/books/{book_id}/reviews/{review_id}`: 본인 리뷰 삭제
- `GET /api/books/my-reviews`: 로그인 회원이 작성한 전체 리뷰 목록 조회
- `GET /api/books/badges/list`: 범용 10종 공감 뱃지 마스터 목록 조회

### 7-4. 회원 및 인증 (`/api/auth`)
- `GET /api/auth/me`: 내 프로필 조회 (닉네임, 선호 연령대 등)
- `GET /api/auth/check-nickname`: 닉네임 중복 여부 확인
- `PATCH /api/auth/me`: 프로필 수정 (닉네임, `preferred_child_age` 등)
- `POST /api/auth/me/agreements`: 약관 및 마케팅 동의 저장
- `DELETE /api/auth/me`: 회원 탈퇴 처리

### 7-5. 내 책장 / 위시리스트 (`/api/wishlists`)
- `GET /api/wishlists`: 로그인 회원의 찜 목록 조회
- `POST /api/wishlists`: 도서 찜 추가
- `DELETE /api/wishlists/{wishlist_id}`: 도서 찜 해제
- `POST /api/wishlists/check`: 다건 도서 찜 여부 일괄 확인

### 7-6. 운영·동기화·자동화 (`/api/threads`, `/api/sync`)
- `GET/POST /api/threads/trigger-weekly`: 주간 Threads 시안 생성 트리거
- `GET/POST /api/threads/approve-text`, `/api/threads/approve`: 텔레그램 승인 페이지 및 제출 처리
- `POST /api/threads/republish/{feed_id}`: 특정 피드 재발행
- `POST /api/sync/childbook/recommendations`: 추천 도서 데이터 동기화

---

## 8. 데이터 시스템 구조 (Supabase)

### 8-1. 지원 공공도서관 (전국 13개, ㄱㄴㄷ 순)
| 도서관명 | 기관코드 (Data4Library) |
| :--- | :--- |
| 광주광역시립무등도서관 | `124003` |
| 부산광역시 강서기적의도서관 | `126156` |
| 서울특별시교육청서울시립어린이도서관 | `111017` |
| 손기정 어린이도서관 | `111498` |
| 송파어린이도서관 | `111117` |
| 수원시립호매실도서관 | `141552` |
| 수지도서관 | `141079` |
| 아이꿈 작은도서관 | `726304` |
| 울산도서관 | `131080` |
| 판교도서관 (기본값) | `141231` |
| 평택시립장당도서관 | `141513` |
| 하남시 위례도서관 | `141636` |
| 한밭도서관 | `125003` |

### 8-2. 주요 테이블 구조 (RLS 적용)

1. **`childbook_items`** (도서 마스터)
   - 기본 정보: `id`, `title`, `author`, `publisher`, `isbn` (UNIQUE), `category`, `age` (`0-3`, `4-7`, `8-12`, `13+`), `image_url`, `vol`, `keywords`
   - 미리보기·메타: `page_count`, `text_level`, `preview_urls` (`TEXT[]`), `national_loan_count`
   - 큐레이션·노출: `curation_tag`, `is_hidden`, `created_at`, `updated_at`
2. **`book_library_info`** (도서관별 소장·청구기호 매핑)
   - `book_id` (FK → `childbook_items`), `library_name`, `callno` (도서관별 청구기호 단일 소스)
3. **`members`** (회원 프로필 — `auth.users` 트리거 자동 생성)
   - `id` (UUID, PK), `email`, `nickname` (자동 생성 및 UNIQUE), `profile_image_url`, `provider` (`kakao`/`google`), `provider_id`
   - `preferred_child_age` (`0-3`, `4-7`, `8-12`, `13+` 또는 `NULL`)
   - `agreed_to_terms`, `agreed_to_privacy`, `agreed_to_marketing`, `created_at`, `updated_at`
4. **`wishlists`** (내 책장 찜 목록)
   - `id`, `user_id` (FK → `members`), `book_id` (FK → `childbook_items`), `created_at`, `UNIQUE(user_id, book_id)`
5. **`book_reviews`** (부모 평점·공감 뱃지·한줄평)
   - `id` (UUID), `book_id`, `user_id`, `nickname`, `child_age`, `rating` (`1.0~5.0`), `selected_badges` (`TEXT[]`), `content`, `is_ai_generated` (내부 관리용, UI 비노출), `created_at`, `UNIQUE(user_id, book_id)`
6. **`threads_feeds`** (Threads 자동 발행 이력 및 스케줄 관리)
   - `id`, `title`, `content`, `image_urls`, `card_descriptions`, `book_ids`, 승인/스케줄 컬럼, `created_at`, `published_at`

### 8-3. 데이터 보정 & 운영 플로우
- **청구기호 매칭**: ISBN 기준 1차 매칭 후 도서관별 스크래핑/API 수집 → `book_library_info` 적재
- **사용자 오류 신고**: 도서 상세 페이지 내 구글 폼 제출 → 운영자 검토 후 Supabase DB 반영

---

## 9. 성능 최적화 전략

### 캐싱 및 병렬 처리
- **홈 화면 ISR**: `revalidate = 3600` (1시간 정적 캐싱) + 도서관 조인 생략으로 초기 TTFB 최소화
- **실시간 대출 상태 API**: 인메모리 캐시 **3분 TTL** + 주기적 만료 캐시 GC + `asyncio.Semaphore(25)` 기반 1페이지(24권) 동시 병렬 처리
- **클라이언트 캐싱**: React Query (`staleTime` 2~3분, `keepPreviousData`)로 책장·리뷰·대출 상태 재요청 최소화

### 렌더링 및 UX 최적화
- 무한 스크롤 (24권 단위) 및 `PageLoader` 브랜드 로딩 UI 일관 적용
- 이미지 최적화: Next.js `Image` + `sizes` 속성 + 알라딘 CDN `preconnect` / `dns-prefetch`
- CORS 화이트리스트 및 정밀 정규식 매칭으로 `checkjari.com` 및 프로젝트 전용 프리뷰 도메인만 허용

---

## 10. 배포 전략 (Deployment Strategy)

### 브랜치 전략
- **`dev` 브랜치**: 개발 및 Vercel Preview 검증용
- **`main` 브랜치**: 상용 프로덕션 배포용

### 배포 프로세스
1. `dev` 브랜치에 기능 개발 및 푸시 → Vercel Preview 환경 자동 배포 및 QA 검증
2. 검증 완료 및 승인 후 `main` 브랜치로 병합
3. `main` 푸시 시 **Vercel(Frontend)** 자동 상용 배포, 백엔드 변경 시 `./deploy_to_aws.sh`로 **AWS Lightsail(Backend)** 동기화 및 재시작
4. 이슈 발생 시 이전 커밋으로 즉시 롤백

---

## 11. 알려진 제약사항 및 향후 과제

### 현재 제약사항
- **지원 도서관 범위**: 현재 전국 13개 대표 공공도서관 지원 (지역별 추가 요청에 따라 순차 확장 중)
- **외부 API 의존성**: 정보나루(Data4Library) API 점검 또는 한도 초과(302 리다이렉트) 시 `확인중` 상태로 graceful fallback 처리
- **대출 정보 시차**: 실시간 조회 결과는 3분 단위 인메모리 캐시 적용
- **오류 신고 수동 처리**: 사용자 제보 접수 후 운영자가 수동 검증 및 DB 보정 수행

### 향후 확장 과제
- 전국 공공도서관 지원 지속 확대 및 도서관별 소장 데이터 자동 갱신 고도화
- 큐레이션·내 책장 카카오톡 공유 카드(OG 이미지) 고도화 및 바이럴 루프 강화
- 부모 리뷰 커뮤니티 활성화 및 연령·상황별 개인화 추천 정교화
- 오류 신고 어드민 대시보드/자동화 파이프라인 도입
