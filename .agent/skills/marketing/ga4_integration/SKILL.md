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

## 4. 리포팅 스킬 (Reporting)

- **클린 데이터 제공**: 개발 트래픽을 제거한 '순수 사용자 트래픽' 보고서 작성
- **인사이트 도출**: 단순히 수치를 나열하지 않고, 인당 페이지 뷰 등을 통해 사용자 참여도를 해석하여 제공

---
*마지막 업데이트: 2026-01-21*
