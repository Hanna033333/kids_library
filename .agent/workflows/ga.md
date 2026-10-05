---
description: Google Analytics 4(GA4) 데이터를 Python SDK로 추출 및 분석하여 NSM, 회원가입 수, 유저 검색어 순위, 채널별 성과, 전환 이벤트를 리포팅하고 그로스 액션을 제안하는 워크플로우
---

# 📊 /ga 구글 애널리틱스(GA4) 성과 분석 워크플로우

이 워크플로우는 사용자가 `/ga` 슬래시 커맨드를 호출했을 때, **GA4 API를 통해 서비스 핵심 지표(NSM, 신규 회원가입 수, 유저 실검색어 리스트, 유입 채널, 전환 이벤트 등)를 자동 수집·분석하고 마케팅/제품 개선 액션을 도출**하는 절차입니다.

---

## 🎯 핵심 지표 체계 (Metrics Framework)

* **🎯 NSM (North Star Metric)**: **도서 상세 페이지 DAU** (`/book/:id` 유니크 방문자 수)
* **👤 신규 회원가입 (Sign-ups)**: 신규 가입자 수 (`sign_up` 커스텀 이벤트 및 DB 신규 계정 수)
* **🔍 유저 검색어 (Search Queries)**: 실제 유저가 입력한 검색 키워드 Top 리스트 (`pagePath`의 `q=` 파라미터 파싱)
* **📈 트래픽 지표**: Active Users, New Users, Sessions, Page Views, Avg Engagement Duration, Bounce Rate
* **🚦 채널 지표**: Threads, Naver Blog, Organic Search (Naver/Google), Direct, Kakao 등
* **⚡ 전환 이벤트**: `click_buy_kyobo`(구매 클릭), `toggle_save_book`(도서 찜), `sign_up`(회원가입) 등

---

## ⚙️ 분석 실행 환경 및 필수 설정

| 항목 | 경로 및 값 |
|---|---|
| **GA4 Property ID** | `518474196` |
| **서비스 계정 키 파일** | `/Users/1004823/Desktop/kids_library/ga_service_account.json` |
| **Python 실행기** | `/Users/1004823/Desktop/kids_library/backend/venv/bin/python3` |
| **SDK 패키지** | `google-analytics-data` (`backend/venv`에 설치됨) |

> ⚠️ 반드시 시스템 `python3` 대신 `backend/venv/bin/python3`를 사용하여 실행합니다.

---

## 🔄 워크플로우 4단계 실행 절차

```
[Step 1. 분석 기간 및 목적 파악]
  - 기본: 최근 7일 또는 저번주 vs 전전주 비교
  - 옵션: 배포 전후 비교, 스레드/블로그 유입 집중 분석 등
       ⬇
[Step 2. GA4 Python SDK 쿼리 실행 & 데이터 정제]
  - 스크래치 폴더에 임시 분석 스크립트 작성 및 실행
  - 내부 개발 트래픽(성남/용인 Desktop 등) 분리 및 순수 유저 데이터 추출
  - 검색어(`q=`) 디코딩 및 회원가입(`sign_up`) 이벤트 집계
       ⬇
[Step 3. 심층 분석 & 지표 시각화]
  - NSM 달성도, 신규 가입 수, 인기 검색어 순위, 채널별 전환율 분석
       ⬇
[Step 4. 성과 보고서 작성 및 그로스 액션 제안]
  - 표준 리포트(핵심 지표 -> 가입/검색어 -> 채널/콘텐츠 -> 실행 액션 플랜) 출력
```

---

## 🛠️ [Step 1] 분석 기간 및 옵션 파악

사용자 입력 형태에 따라 유연하게 기간과 대상을 설정합니다:
1. `/ga` (단독 호출): **최근 7일간의 일별 추이 및 직전 동기간 대비 비교**
2. `/ga 저번주`: **직전 주(월~일) vs 전전 주(월~일) 주간 정기 성과 비교**
3. `/ga 배포 [날짜]`: **특정 배포일 전후 지표 비교 (예: 10/1 배포 전후)**
4. `/ga [채널명]`: **특정 유입 채널(예: `스레드`, `네이버 블로그`) 심층 드릴다운**

---

## 🐍 [Step 2] 데이터 수집 스크립트 작성 및 실행

에이전트는 스크래치 경로(`~/.gemini/antigravity-ide/scratch/ga_query.py` 등)에 분석 스크립트를 작성하고 실행합니다.

### 💡 표준 쿼리 템플릿 구조

```python
import os
import urllib.parse
from collections import Counter
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest, OrderBy, FilterExpression, Filter
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/1004823/Desktop/kids_library/ga_service_account.json"
PROPERTY_ID = "518474196"
client = BetaAnalyticsDataClient()

def query_ga4(start_date, end_date, dimensions, metrics, dimension_filter=None, order_bys=None, limit=50):
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=dimension_filter,
        order_bys=order_bys,
        limit=limit,
    )
    response = client.run_report(request)
    return [
        {**{dim: row.dimension_values[i].value for i, dim in enumerate(dimensions)},
         **{met: row.metric_values[i].value for i, met in enumerate(metrics)}}
        for row in response.rows
    ]
```

### 🧼 데이터 정제 및 파싱 핵심 원칙
1. **신규 회원가입 수 추출**:
   - `eventName = 'sign_up'` 이벤트 수(`eventCount`)를 쿼리하거나, 필요 시 Supabase `profiles` 테이블의 신규 유저 생성 수와 교차 검증합니다.
2. **CSR 실시간 검색어 파싱**:
   - React SPA 검색 특성상 기본 `searchTerm` 대신 `pagePath`에서 `q=` 쿼리 파라미터를 추출하고 `urllib.parse.unquote()`로 디코딩하여 빈도수를 집계합니다:
     ```python
     # 검색어 파싱 예시
     search_pages = query_ga4(start_date, end_date, ["pagePath"], ["screenPageViews", "activeUsers"])
     search_counts = Counter()
     for row in search_pages:
         path = row["pagePath"]
         if "q=" in path:
             parsed = urllib.parse.urlparse(path)
             params = urllib.parse.parse_qs(parsed.query)
             if "q" in params and params["q"][0].strip():
                 keyword = urllib.parse.unquote(params["q"][0].strip())
                 search_counts[keyword] += int(row["screenPageViews"])
     ```
3. **개발 트래픽 분리**:
   - 성남/용인 Desktop 트래픽의 비정상적 긴 체류 시간이나 다량 PV는 내부 테스트용이므로 일반 모바일/외부 유입과 분리하여 해석합니다.
4. **도서 상세 착지 필터**:
   - `pagePath` contains `/book/` 쿼리를 통해 순수 도서 상세 DAU를 집계합니다.

---

## 📊 [Step 3 & 4] GA4 성과 분석 리포트 출력 포맷

데이터 추출이 완료되면 채팅창에 아래와 같은 표준 리포트 양식으로 결과를 보고합니다.

```markdown
# 📊 GA4 서비스 성과 분석 리포트 ({시작일} ~ {종료일})

### 1️⃣ 핵심 지표 요약 (KPI Overview)
| 지표 | 수치 | 전 기간 대비 | 비고 |
|---|---|---|---|
| **🎯 NSM (도서 상세 DAU)** | **{N}명** | **{+N% / -N%}** | `/book/:id` 유니크 방문자 |
| **👤 신규 회원가입 (Sign-ups)** | **{N}명** | **{+N% / -N%}** | 신규 계정 생성 수 |
| **총 활성 사용자 (Active Users)** | {N}명 | {+N% / -N%} | 순수 방문자 수 |
| **신규 사용자 (New Users)** | {N}명 | {+N% / -N%} | 신규 유입 비중 {N}% |
| **세션 수 (Sessions)** | {N}회 | {+N% / -N%} | 세션당 PV: {N}개 |
| **페이지뷰 (PV)** | {N}회 | {+N% / -N%} | |
| **평균 참여 시간** | {N}초 | {+N% / -N%} | 모바일 평균 {N}초 |

---

### 2️⃣ 유저 검색어 순위 (Top Search Keywords)
> 유저가 직접 입력하여 도서를 탐색한 실시간 검색어 현황입니다.
1. **"{검색어 1}"**: {N}회 검색 ({N}명)
2. **"{검색어 2}"**: {N}회 검색 ({N}명)
3. **"{검색어 3}"**: {N}회 검색 ({N}명)
4. **"{검색어 4}"**: {N}회 검색 ({N}명)
5. **"{검색어 5}"**: {N}회 검색 ({N}명)

---

### 3️⃣ 유입 채널별 성과 (Acquisition Channels)
* **🧵 Threads (스레드)**: {N}세션 / {N}명 (인기 큐레이션: `{테마명}`)
* **📝 Naver Blog (네이버 블로그)**: {N}세션 / {N}명
* **🔍 Organic Search (검색)**: {N}세션 (네이버 {N} / 구글 {N})
* **🔗 Direct / 기타**: {N}세션

---

### 4️⃣ 인기 콘텐츠 & 페이지 Top 5
1. **{페이지 경로 또는 큐레이션명}**: PV {N}회 / {N}명 (평균 체류 {N}초)
2. **{페이지 경로 또는 큐레이션명}**: PV {N}회 / {N}명
...

---

### 5️⃣ 전환 이벤트 및 유저 인터랙션
* **회원가입 완료 (`sign_up`)**: {N}건 (방문자 대비 가입 전환율 {N}%)
* **교보문고 구매 클릭 (`click_buy_kyobo`)**: {N}건 (상세 방문 대비 전환율 {N}%)
* **도서 찜하기 (`toggle_save_book`)**: {N}건
* **도서관 대출상태 조회 (`check_loan_status`)**: {N}건

---

### 💡 6️⃣ 마케팅 & 제품 성장 액션 (Growth Insights)
1. **[검색어 기반 큐레이션]**: {다빈도 검색 키워드를 신규 큐레이션 테마나 홈 배너로 제작 제안}
2. **[가입/전환 최적화]**: {회원가입 및 도서 찜 유도 동선 개선 제안}
3. **[채널/SEO 액션]**: {유입 효율 높은 채널 추가 발행 및 검색 노출 강화}
```

---

## 📌 관련 규칙 및 스킬 참조
* `@.agent/rules/marketing.md` — 마케팅 KPI 및 전환 최적화 정책
* `@.agent/rules/growth_hacker.md` — 데이터 기반 그로스 가설 검증
* `@.agent/skills/marketing/ga4_integration/SKILL.md` — GA4 상세 스킬 문서
