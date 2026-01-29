---
description: 겨울방학 추천도서 캠페인 성과 측정 (GA4)
---

# 겨울방학 캠페인 성과 리포트 워크플로우

이 워크플로우는 `google-analytics-mcp`를 사용하여 겨울방학 캠페인의 핵심 지표를 자동으로 추출합니다.

## 지표 측정 단계

1. **사용자 유입 확인 (Acquisition)**
   - 목표: 유입 경로별 활성 사용자 수 확인
   - 도구: `analytics-mcp.run_report`
   - 디멘션: `sessionSourceMedium`
   - 메트릭: `activeUsers`, `sessions`

2. **도서 클릭 성과 확인 (Activation)**
   - 목표: "겨울방학 섹션" 도서 상세 클릭 수 확인
   - 도구: `analytics-mcp.run_report`
   - 이벤트명: `click_book_detail`
   - 파라미터: `book_title`, `call_number`

3. **재방문율 확인 (Retention)**
   - 목표: 캠페인 기간 내 재방문 사용자 비중 확인
   - 메트릭: `newUsers` vs `activeUsers` 비율 분석

## 실행 방법
`@marketing`에게 다음과 같이 요청하세요:
> "/check_winter_campaign 워크플로우를 실행해서 현재 캠페인 대시보드 요약해줘."
