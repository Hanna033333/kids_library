---
name: ga4-integration
description: Google Analytics 4 연동, 인증 설정 및 데이터 추출 가이드
---

# Google Analytics 4 (GA4) 연동 및 활용 스킬 가이드

본 문서는 `@marketing` 에이전트가 `checkjari.com` 프로젝트의 GA4 데이터를 성공적으로 연결하고 활용하기 위해 수행한 기록을 정리한 것입니다.

---

## 0. 핵심 지표 체계 (Metrics Framework)

> **[2026.05 업데이트]** 서비스 핵심 가치가 "청구기호 로컬 유틸리티"에서 "전국 큐레이션 플랫폼"으로 피봇됨에 따라, 지표 체계를 전면 재정의합니다.
> 네이버 검색을 통한 상세/리스트 직접 착지가 주요 유입 경로이므로, "홈 → 상세 진입률" 기반 퍼널은 실제 트래픽 구조를 반영하지 못합니다.

### 🎯 NSM (North Star Metric)
> **도서 상세 페이지 DAU** — 일별 유니크 도달자 수 (`/book/:id` 페이지 기준)

- 홈·리스트·네이버 검색 등 **모든 유입 경로를 포괄**하는 단일 지표
- GA4에서 `pagePath contains /book/` 필터로 즉시 측정 가능 (추가 이벤트 세팅 불필요)

### 📊 보조 지표 (Supporting Metrics)
| 지표 | 정의 | GA4 측정 방법 |
|---|---|---|
| **액션: 행동 전환 수** | 교보 구매 클릭 + 대출 확인 클릭 합산 | `click_buy_kyobo` 등 커스텀 이벤트 |
| **인게이지먼트: 가입 & 찜** | 신규 회원가입 성공 수 및 도서 찜하기 클릭 수 | `sign_up`, `toggle_save_book` 이벤트 |
| **도서 상세 체류 시간** | `/book/:id` 내 평균 `userEngagementDuration` | `pagePath contains /book/` 필터 |
| **큐레이션 섹션 체류 시간** | 홈 화면 내 큐레이션 스크롤/머무름 | `scroll` 이벤트 분석 |

### 🔄 리텐션 지표
- **목표**: 7일 재방문율 35% 이상
- **산출 방식**: `returning / (new + returning)` 사용자 비율
- **채널별 비교**: Naver 검색 유입 vs 직접 접속 vs 레퍼럴 채널별 리텐션 차이 비교

---

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

---

## 2. 데이터 추출 기술 (Data Extraction)

### 📈 API 직접 호출 (Python SDK)
- MCP 서버의 초기화 지연(Wait time)을 방지하기 위해 `google-analytics-admin` 및 `google-analytics-data` 라이브러리를 직접 사용하는 스크립트 활용
- **주요 활용 지표**:
    - `activeUsers`, `sessions`, `screenPageViews`
    - `pagePath` (인기 페이지 분석 — `/book/:id` 우선 확인)
    - `userEngagementDuration` (체류 시간 분석)

---

## 3. 데이터 정제 및 필터링 (Data Cleaning)

### 🧼 개발 트래픽 제외 로직
- **지역/기기 필터링**: 성남/용인 지역의 Desktop 트래픽을 API 쿼리 단계에서 `FilterExpression`을 통해 동적으로 제외
- **내부 트래픽 필터(GA4)**: GA4 설정 내 'Internal Traffic' 필터를 '테스트'에서 '활성'으로 전환 가이드

### 📱 모바일 기기 제외 (비밀 주소 방식)
- IP가 가변적인 모바일 환경을 위해 URL 파라미터를 이용한 트래킹 차단 구현
- **주소**: `https://checkjari.com/?ignore=true`
- **구현**: `localStorage`에 `checkjari_ignore_tracking` 플래그를 심고, `layout.tsx` 및 `analytics.ts`에서 해당 플래그 확인 시 `gtag` 실행을 중단함

---

## 4. 리포팅 기준 (Reporting Standard)

> GA4 분석 보고서를 작성할 때는 반드시 아래 순서와 기준을 따릅니다.

### ① NSM 확인 (최우선)
- **도서 상세 페이지 DAU** (`/book/:id` 유니크 방문자): 전일 대비, 전주 대비 추이
- 유입 경로별 분해 (Naver 검색 / 직접 / 레퍼럴)

### ② 보조 지표 확인
- 교보 구매 클릭 수 (`click_buy_kyobo` 이벤트)
- 도서 상세 평균 체류 시간

### ③ 리텐션 확인
- 7일 재방문율: `returning / (new + returning)`
- 채널별 리텐션 비교 (고품질 채널 식별)

### ④ 콘텐츠 성과 확인 (큐레이션 피봇 이후 신규)
- 인기 도서 상세 페이지 Top 10 (`pagePath` 기준)
- 홈 화면 큐레이션 섹션 스크롤 깊이

### ⑤ 데이터 정제 원칙
- **내부 트래픽 필수 제외**: Seongnam/Yongin Desktop 등 내부 개발 트래픽 필터링 후 순수 유저 데이터만 분석

### ⑥ CSR 검색어 우회 분석 기법 (신규)
- React State 기반의 CSR 검색 환경에서는 기본 `searchTerm` 디멘션이 빈 문자열(`''`)로 수집되는 이슈가 있음.
- 유저 검색어를 트래킹하기 위해 **페이지 경로(`pagePath`)** 중 `q=` 쿼리 스트링 파라미터를 포함한 `/books?q=검색어` 형태의 페이지뷰를 쿼리하여 검색 키워드 수요를 간접 파싱하는 방식을 필수로 활용함.

### ⑦ 마케팅 분석 고도화 5대 실행 가이드 (2026.08 신규)
1. **NSM 중심 Landing 퍼널**: Direct 착지(검색/소셜) 사용자를 감안해 `/book/:id` DAU 중심 퍼널 유지.
2. **채널별 UTM Attribution**: 블로그(`utm_source=naver_blog`), 스레드(`utm_source=threads`), 카카오톡(`utm_source=kakao`) 파라미터 분리 및 전환율 측정.
3. **이벤트 기반 액션 파악**: `click_buy_kyobo`, `check_loan_status`, `toggle_save_book`, `share_kakao` 커스텀 이벤트 추적.
4. **SEO 기회 키워드 공략**: 검색 결과 노출 대비 CTR 낮은 키워드 타이틀/메타 문구 A/B 테스트.
5. **데이터 회고 루프**: 주간 지표 미달 시 CTA/제목 즉시 수정, 달성 시 관련 채널 콘텐츠 추가 발행.

---

## 5. 레거시: 구(舊) 퍼널 분석 기준 (참고 보존)

> 아래는 이전 버전의 분석 기준으로, 현재는 사용하지 않습니다. 이전 데이터와의 비교가 필요할 때만 참조하세요.

- 홈 (Home) → 리스트 진입 (List) → 책 상세 진입 (Book Detail) → 구매 클릭 (Buy Click)
- **폐기 이유**: 네이버 검색을 통한 직접 착지가 주요 유입이어서 "홈 → 상세 진입률"이 실제 트래픽을 대표하지 못함

---
---

## 6. 주간 GA4 리포트 실행 방법 (API 직접 조회 방식)

> **[2026-08-31 추가]** 브라우저 GUI 없이 Python SDK로 GA4 데이터를 직접 조회하고 아티팩트 리포트를 생성하는 표준 절차입니다.

### ✅ 전제 조건
| 항목 | 값 |
|---|---|
| 서비스 계정 키 파일 | `/Users/1004823/Desktop/kids_library/ga_service_account.json` |
| GA4 속성 ID (숫자형) | `518474196` |
| 측정 ID (gtag용, API엔 불필요) | `G-FG2WYB82L9` |
| Python 실행 환경 | `backend/venv/bin/python3` |
| SDK | `google-analytics-data` (venv에 설치 완료) |

> ⚠️ `python3` 또는 `pip3`로 직접 실행하면 "externally managed" 오류가 남. 반드시 `backend/venv/bin/python3`를 사용할 것.

---

### 📋 분석 날짜 범위 계산
- **저번주**: 직전 월요일 ~ 직전 일요일 (예: 오늘이 8/31이면 `2026-08-24 ~ 2026-08-30`)
- **전전주**: 그 이전 주 (비교 기준)
- 날짜는 `YYYY-MM-DD` 형식으로 스크립트 상단에 고정 입력

---

### 🐍 주간 분석 스크립트 구조

스크립트는 `/private/tmp/` 또는 스크래치 디렉토리에 임시 생성 후 실행. 분석 섹션 구성:

```
1. 핵심 지표 요약  — activeUsers, newUsers, sessions, screenPageViews,
                    averageSessionDuration, bounceRate (저번주 vs 전전주)
2. 인기 페이지 Top 10 — pagePath, pageTitle, PV, activeUsers, 체류시간
3. 유입 채널 분석  — sessionDefaultChannelGrouping (저번주 vs 전전주)
4. 요일별 PV 패턴  — date + dayOfWeek 기준 7일 분포
5. 기기별 분석    — deviceCategory (mobile/desktop 비율, 이탈률)
6. 신규 vs 재방문  — newVsReturning (체류시간 차이에 주목)
7. 지역별 상위 5  — country + region
```

**핵심 패턴 — 복수 DateRange 사용 시 주의:**
- `date` 디멘션과 복수 `date_ranges` 동시 사용 시 `dimension_values[1]`이 `"date_range_0"` / `"date_range_1"` 문자열로 반환됨 (int 변환 불가)
- ✅ **권장 방식**: 날짜 범위별로 **쿼리를 분리**하여 각각 호출 후 Python에서 합산

**FilterExpression 필터 적용 패턴:**
```python
from google.analytics.data_v1beta.types import Filter
StringFilter = Filter.StringFilter  # 별도 import 없이 내부 클래스 접근

dimension_filter=FilterExpression(filter=Filter(
    field_name="sessionDefaultChannelGrouping",
    string_filter=StringFilter(
        match_type=StringFilter.MatchType.EXACT,
        value="Referral",
    )
))
```

---

### 🔍 Referral 유입 심층 분석 방법

Referral 세션이 갑자기 발생했거나 소스가 궁금할 때:

```python
# 1. 소스별 세션 분해
dimensions=["sessionSource", "sessionMedium", "sessionCampaignName"]
metrics=["sessions", "activeUsers", "screenPageViews", "averageSessionDuration", "bounceRate"]
# + FilterExpression으로 sessionDefaultChannelGrouping = "Referral" 필터

# 2. 랜딩 페이지 × 소스 교차 분석
dimensions=["landingPage", "sessionSource"]
metrics=["sessions", "activeUsers", "screenPageViews", "averageSessionDuration"]
```

> ⚠️ **GA4 `landingPage` 디멘션은 쿼리파라미터를 자동 제거**하고 path만 기록함.
> `/books?curation=세계역사` → `landingPage = /books`로 찍힘.
> 만약 `/books`가 아닌 `/`로 찍혔다면 실제로 홈에 착지한 것.

---

### ⚠️ Threads 링크 관련 알려진 이슈 (2026-08-31 발견)

- **문제**: `checkjari.com/books?curation=세계역사&sort=confidence_score_desc` 링크를 스레드에 게시했는데 GA에서 대부분 `/`(홈)으로 착지 기록됨
- **원인**: Threads 인앱브라우저가 한글 퍼센트 인코딩(`%EC%84%B8...`) 쿼리파라미터를 손실하거나, 링크 카드(OG 미리보기) 탭 시 도메인 루트로 이동하는 것으로 추정
- **해결책**: 스레드 게시물에는 반드시 **슬러그 기반 URL** 사용
  ```
  ❌ /books?curation=세계역사&sort=confidence_score_desc
  ✅ /collections/curation/world-history
  ```
- **자동화 완료**: 스레드 발행 완료 후 텔레그램에 `/collections/curation/{slug}` 형태의 링크가 자동 메시지로 전송됨 (`api/threads.py` 3곳에 반영)

---

### 📊 아티팩트 리포트 생성

분석 완료 후 `artifact-design` 스킬을 로드하고 HTML 아티팩트로 시각화:
- **KPI 카드 그리드** (3열): 핵심 6지표 + 전전주 대비 증감
- **채널 바 차트**: 전전주 기준선 표시 + 신규/기존 증감
- **요일별 PV 바 차트**: CSS 인라인 비율 바 (max PV 기준 100%)
- **인기 페이지 테이블**: path + 제목 + PV + 유저 + 체류시간
- **기기/신규재방문 카드**: 인라인 비율 바

---

### 📌 주간 리포트 실행 명령어 요약

```bash
# 스크립트 작성 후 실행
/Users/1004823/Desktop/kids_library/backend/venv/bin/python3 /path/to/ga4_analysis.py
```

*마지막 업데이트: 2026-08-31*
