---
name: Curated Book Section Management
description: A guide for adding and managing curated book sections (e.g., Caldecott, Winter Vacation), covering planning, data preparation, and implementation.
---

# 📚 큐레이션 섹션 관리 가이드 (Curated Section Management)

이 스킬은 '칼데콧 수상작'과 같이 특별한 테마의 도서 컬렉션을 서비스에 추가할 때 따르는 표준 절차입니다.

## 1. 기획 및 카피라이팅 (Planning & Copywriting)

### 타이틀 및 메시지 선정
- **규칙**: 섹션의 타이틀과 서브 텍스트는 **[마케팅 팀장 페르소나](file:///Users/1004823/Desktop/kids_library/.agent/rules/marketing.md)**의 제안을 따릅니다.
- **목표**: 단순한 정보 전달을 넘어 학부모의 니즈를 자극하는 '셀링 포인트'를 포함해야 합니다.
- **예시 (칼데콧)**:
  - **타이틀**: "칼데콧 수상작" (명확하고 권위 있는 키워드)
  - **서브 텍스트**: "미국 도서관 사서들이 엄선한 최고의 그림책" (신뢰성 강조)

## 2. 데이터 준비 및 품질 관리 (Data Preparation)

### 이미지 품질 (Image Quality)
- **필수 사항**: 도서 표지 이미지는 반드시 **고해상도(`cover500`)**를 사용해야 합니다.
- **금지 사항**: 저해상도 썸네일(`coversum`)은 메인 UI의 퀄리티를 떨어뜨리므로 절대 사용하지 않습니다.
- **방법**: 알라딘 API 등을 통해 데이터 수집 시, 이미지 URL 패턴을 `cover500`으로 변경하거나 해당 해상도의 이미지를 우선적으로 확보합니다.

### 도서 검색 및 매칭 (ISBN Search Strategy)
- **원서 기반 검색 (For Translated Works)**:
  - 칼데콧 수상작처럼 **해외 원작이 있는 경우**, 한국어 번역명으로 검색하면 정확한 ISBN을 찾기 어렵거나 절판된 구판이 검색될 수 있습니다.
  - **해결책**: **원서 제목(English Title)**과 **저자명**을 조합하여 검색한 뒤, 국내 번역본의 ISBN을 매칭하는 방식을 사용합니다.
  - *Note: 이 방식은 칼데콧이나 뉴베리 등 해외 수상작 컬렉션 구축 시 특히 유효합니다.*

### 카테고리화 (Categorization)
- **SQL 기반 분류**:
  - 수집된 도서 데이터는 `childbook_items` 테이블 등에 저장된 후, SQL 쿼리를 통해 적절한 `category` 태그를 부여해야 합니다.
  - 예: `UPDATE childbook_items SET category = '칼데콧' WHERE ...`

## 3. 디자인 및 UI 구현 (Design & Implementation)

### UI 일관성 유지
- **기존 섹션 참조**: 새로운 섹션은 기존의 '겨울방학 추천 도서', '어린이 도서 연구회' 섹션과 **동일한 UI 구조**를 유지해야 합니다.
- **컴포넌트 재사용**: `BookList`, `BookCard` 등 이미 검증된 공통 컴포넌트를 사용하여 개발 효율성과 사용자 경험의 일관성을 확보합니다.

### 구현 체크리스트
- [ ] **Data Fetching**: `lib/home-api.ts` 등에 해당 큐레이션을 위한 Fetch 함수 추가
- [ ] **Component Update**: `HomePageClient.tsx`에 새로운 섹션 추가
- [ ] **Responsiveness**: 모바일/태블릿/데스크탑 환경에서의 스크롤 및 배치 확인
- [ ] **Link Routing**: "더보기" 클릭 시 해당 큐레이션 필터가 적용된 목록 페이지(`/books?curation=xxx`)로 이동

## 4. 검증 및 배포 (Verification)
- **데이터 무결성 확인**: 이미지가 깨지지 않는지, ISBN이 정확한지 SQL 조회 및 UI 확인
- **가독성 점검**: [디자인 팀장 페르소나](file:///Users/1004823/Desktop/kids_library/.agent/rules/design.md) 기준에 맞춰, 타이틀과 책 정보가 서가 환경(모바일)에서도 잘 보안지 확인
