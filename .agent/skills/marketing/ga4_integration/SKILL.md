---
name: ga4-integration
description: Google Analytics 4 연동, 인증 설정 및 데이터 추출 가이드
---

# Google Analytics 4 (GA4) 연동 및 활용 스킬 가이드

본 문서는 `@marketing` 에이전트가 `checkjari.com` 프로젝트의 GA4 데이터를 성공적으로 연결하고 활용하기 위해 수행한 기록을 정리한 것입니다.

## 1. 인프라 및 인증 설정 (Infrastructure & Auth)

### 🛠️ MCP 서버 설정 (`mcp_config.json`)
- `analytics-mcp` 서버를 `pipx`를 통해 설치하고 환경 변수를 구성했습니다.
- **핵심 설정**:
    - `GOOGLE_APPLICATION_CREDENTIALS`: 서비스 계정 키 파일 경로 설정
    - `GOOGLE_PROJECT_ID`: GCP 프로젝트 ID (`kids-library-483408`)

### 🔑 Google 인증 및 권한 해결
- **gcloud CLI 인증**: `gcloud auth application-default login`을 통해 로컬 인증 환경 구축
- **Scope 문제 해결**: 단순 로그인 시 애널리틱스 권한이 누락될 수 있어 아래 명령어로 권한을 강제 갱신함
  ```powershell
  gcloud auth application-default login --scopes="https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform"
  ```
- **계정 권한**: GA4 관리자 페이지에서 `hannalife03@gmail.com` 계정에 '뷰어' 이상의 권한이 부여되어 있는지 확인 루틴 수립

## 2. 데이터 추출 기술 (Data Extraction)

### 📈 API 직접 호출 (Python SDK)
- MCP 서버의 초기화 지연(Wait time)을 방지하기 위해 `google-analytics-admin` 및 `google-analytics-data` 라이브러리를 직접 사용하는 스크립트 활용
- **주요 활용 지표**:
    - `activeUsers`, `sessions`, `screenPageViews`
    - `pagePath` (인기 페이지 분석)
    - `userEngagementDuration` (체류 시간 분석)

## 3. 데이터 정제 및 필터링 (Data Cleaning)

### 🧼 개발 트래픽 제외 로직
- **지역/기기 필터링**: 성남/용인 지역의 Desktop 트래픽을 API 쿼리 단계에서 `FilterExpression`을 통해 동적으로 제외
- **내부 트래픽 필터(GA4)**: GA4 설정 내 'Internal Traffic' 필터를 '테스트'에서 '활성'으로 전환 가이드

### 📱 모바일 기기 제외 (비밀 주소 방식)
- IP가 가변적인 모바일 환경을 위해 URL 파라미터를 이용한 트래킹 차단 구현
- **주소**: `https://checkjari.com/?ignore=true`
- **구현**: `localStorage`에 `checkjari_ignore_tracking` 플래그를 심고, `layout.tsx` 및 `analytics.ts`에서 해당 플래그 확인 시 `gtag` 실행을 중단함

## 4. 리포팅 및 지표 관리 (Reporting & Metrics)

### 📊 표준 퍼널 분석 (Funnel Analysis)
- 모든 분석 보고서에는 아래의 표준 퍼널 단계별 전환율을 포함합니다.
    1. **홈 (Home)**: 메인 페이지 진입
    2. **리스트 진입 (List)**: 검색 결과 또는 큐레이션 리스트 노출
    3. **책 상세 진입 (Book Detail)**: `view_book_detail` 이벤트 발생
    4. **구매 클릭 (Buy Click)**: `click_buy_kyobo` 등 외부 구매 링크 클릭

### 🔄 리텐션 관리 (Retention)
- **리텐션율 산출**: `returning / (new + returning)` 사용자 비율을 주기적으로 분석합니다.
- **채널별 비교**: 유입 경로(Source/Medium)별로 리텐션 차이를 비교하여 양질의 트래픽을 유도하는 채널을 식별합니다. (예: Naver Cafe vs Referral)

### 📈 데이터 정제 원칙
- **내부 트래픽 제외**: 분석 시 반드시 내부 개발 트래픽(Seongnam/Yongin Desktop 등)을 필터링하여 순수 유저 데이터만 제공합니다.

---
*마지막 업데이트: 2026-01-21*
