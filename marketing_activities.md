# Marketing Activities & Status

현재 진행 중인 마케팅 활동, 광고, SEO 및 데이터 분석 현황을 정리한 문서입니다.

## 1. 진행 중인 캠페인 (Campaigns)

### ❄️ 겨울방학 추천도서 캠페인
겨울방학 시즌을 맞아 학부모와 어린이가 양질의 도서를 쉽게 찾을 수 있도록 큐레이션된 섹션을 운영합니다.

*   **목표**: '겨울방학 추천도서' 섹션 유입 증대 및 도서 상세 조회(Conversion) 유도
*   **Customer Journey**: `유입(Acquisition)` → `도서 클릭(Activation)` → `재방문(Retention)`
*   **성과 측정**:
    *   **도구**: Google Analytics 4 (GA4)
    *   **워크플로우**: `/check_winter_campaign` (자동화된 성과 리포트 생성)
    *   **주요 지표 (KPIs)**:
        *   `sessionSourceMedium` (유입 경로 분석)
        *   `click_book_detail` (도서 상세 클릭 수)
        *   `Active Users` vs `New Users` (재방문율 파악)

## 🔄 Phase 2: The "Click Pivot" (Current Focus)
*Goal: Validate acquisition by removing "App" friction.*

### 1. New Core Message: "Anti-App"
- **Problem**: Users ignore the post because they fear "App Install" friction.
- **Solution**: Explicitly scream **"No Install, No Login"**.

### 2. Action Plan (Copy Testing)
- **Angle A (Convenience)**: "Don't install apps. Just bookmark." -> Target: Lazy/Busy Moms.
- **Angle B (FOMO)**: "Librarian's Secret List." -> Target: Edu-focused Moms.
- **Angle C (Pain)**: "Don't stand in line at the kiosk." -> Target: Library Goers.

### 3. Measurement (UTM)
- All new posts MUST use UTM links.
- `?utm_source=[channel]&utm_medium=social&utm_campaign=[angle]`
- Example: `checkjari.com/?utm_source=momcafe&utm_medium=social&utm_campaign=angle_a`

---

## 2. 채널 및 광고 전략 (Channels & Ads)

### 🟢 네이버 검색광고 (Naver Search Ads)
판교 지역 학부모를 타겟으로 한 검색 광고 집행 준비 단계입니다.

*   **상태**: 집행 준비 중 (Setup Phase)
*   **타겟 키워드**: `판교 도서관`, `어린이 도서 추천`, `청구기호 찾기` 등
*   **액션 아이템**:
    *   [ ] UTM 파라미터 전략 수립 및 세팅
    *   [ ] 키워드 성과 모니터링 환경 구축

### 📢 커뮤니티 바이럴 (Community Viral)
*   **타겟**: 판교 지역 맘카페, 아파트 커뮤니티, 지역 기반 온라인 그룹
*   **전략**: '도서관 청구기호 찾기의 어려움'을 해결해주는 유용한 툴로서 자연스러운 바이럴 유도
*   **기능 지원**:
    *   [ ] 카카오톡 공유하기 기능 도입 (개발 논의 중)

---

## 3. SEO (검색 엔진 최적화)

네이버와 구글에서의 유기적 유입(Organic Traffic)을 늘리기 위한 테크니컬 마케팅 활동입니다.

### 🟢 네이버 (Naver Search Advisor)
*   **완료 사항**:
    *   `robots.txt` 설정 최적화
    *   메타 태그(Open Graph, Description) 적용
    *   사이트 소유권 확인 완료
*   **진행 중**:
    *   '수집 제한' 이슈 모니터링 및 해결
    *   도서 상세 페이지 수집 활성화

### 🔵 구글 (Google Search Console)
*   **완료 사항**:
    *   사이트맵(sitemap.xml) 제출
    *   주요 페이지 인덱싱 요청
*   **진행 중**:
    *   구조적 데이터(Structured Data) 마크업 적용을 통한 리치 스니펫 노출 유도

---

## 4. 데이터 분석 인프라 (Analytics Infra)

*   **GA4 연동**: 웹사이트와 Google Analytics 4 연동 완료
*   **맞춤 이벤트**: 도서 클릭, 검색, 카테고리 필터 사용 등 핵심 사용자 행동 이벤트 정의 및 수집
*   **운영 도구**:
    *   `/verify_prod`: 상용 배포 상태 및 정책 검증
    *   `/check_winter_campaign`: 마케팅 캠페인 성과 측정
