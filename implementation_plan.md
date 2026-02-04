# 칼데콧 수상작 섹션 구현 계획

## 목표
2000년부터 2026년까지의 칼데콧(Caldecott) 수상작 목록을 데이터베이스에 통합하고, 알라딘 API와 도서관 크롤링을 통해 풍부한 도서 정보를 제공하는 전용 페이지를 구축합니다.

## 사용자 검토 필요
없음.

## 제안된 변경 사항

### 데이터수집 파이프라인 (Data Pipeline)
기존 수동 입력 방식을 개선하여 알라딘 API와 도서관 크롤링을 활용한 자동화된 파이프라인을 구축합니다.

#### 단계 1: 데이터 준비
- `caldecott_winners.md`의 내용을 바탕으로 기본 정보(연도, 제목, 한글 제목, 작가)를 담은 JSON 파일 생성 (`caldecott_base.json`)

#### 단계 2: 알라딘 API 연동 (데이터 보강)
- **스크립트**: `backend/fetch_caldecott_aladin.py` (신규)
- **기능**: `caldecott_base.json`을 읽어 알라딘 API로 검색
- **수집 정보**: ISBN, 고화질 표지 이미지 URL, 출판사, 책 소개(Description)
- **결과**: `caldecott_enriched.json` 생성

#### 단계 3: 판교도서관 크롤링 (소장 정보)
- **스크립트**: `backend/crawl_caldecott_callno.py` (신규, 기존 `crawl_pangyo_callno_v2.py` 참고)
- **기능**: `caldecott_enriched.json`의 ISBN 또는 제목/작가를 사용하여 판교도서관 소장 여부 및 청구기호 수집
- **결과**: `caldecott_final.json` 생성

#### 단계 4: DB 적재
- **스크립트**: `backend/insert_caldecott_final.sql` (생성)
- **기능**: 최종 JSON 데이터를 `childbook_items` 테이블에 삽입 (태그: `'caldecott'`)

### 백엔드 (API)
#### [신규] [caldecott-api.ts](file:///c:/Users/skplanet/Desktop/kids%20library/frontend/lib/caldecott-api.ts)
- `getCaldecottBooks(client?)` 함수 구현
- `curation_tag = 'caldecott'` 조건으로 조회
- 연도별 로직 추가 (필요 시 `meta` 컬럼 등에 연도 저장하거나 설명 필드 활용)

### UI 컴포넌트
#### [신규] [page.tsx](file:///c:/Users/skplanet/Desktop/kids%20library/frontend/app/caldecott/page.tsx)
- `/caldecott` 페이지 생성
- `CaldecottList` 컴포넌트를 통해 도서 목록 표시 (표지, 제목, 청구기호 등)

#### [수정] [page.tsx](file:///c:/Users/skplanet/Desktop/kids%20library/frontend/app/page.tsx)
- 메인 홈에 "칼데콧 수상작(2000-2026)" 바로가기 배너 추가

## 검증 계획

### 자동화 테스트
- 데이터 수집 스크립트 실행 로그 확인

### 수동 검증
1.  **데이터 정확성**: 알라딘 API 매칭 결과 확인 (특히 영문/한글 제목 매칭)
2.  **크롤링 확인**: 판교도서관 청구기호가 정상적으로 수집/저장되었는지 DB 확인
3.  **UI 확인**: 실제 화면에서 표지 이미지와 정보가 올바르게 렌더링되는지 확인
