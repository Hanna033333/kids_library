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

### 연령대(Age) 매핑 표준 (Elementary Age Mapping)
- **초등 연령 매핑 규격**:
  - 초등학교 1~6학년 대상 도서들을 프론트엔드 연령별 추천 필터 탭 중 **'8~12세'**에 정확하게 표시하기 위해서는, DB `childbook_items.age` 컬럼의 값을 **`'9세부터'`**로 일치시켜 적재해야 합니다.
  - 기획서상의 초등 학년군(예: 초등 1-2학년, 초등 3-4학년 등)은 DB에 삽입할 때 이 규칙에 따라 일괄 `'9세부터'`로 표준화하여 탭 노출 오작동을 원천 예방합니다.

### 카테고리화 (Categorization)
- **SQL 및 파이썬 기반 분류**:
  - 수집된 도서 데이터는 `childbook_items` 테이블에 저장될 때, 분류 속성에 따라 알맞은 `category` 태그(예: `동화`, `그림책`, `과학`, `사회`, `전통` 등)를 부여해야 합니다.
  - 알라딘 API 장르 코드를 기본 매핑하되, 정합성이 떨어지는 책은 `manual_mappings` 등으로 직접 보정합니다.

## 3. 디자인 및 UI 구현 (Design & Implementation)

### UI 일관성 유지
- **기존 섹션 참조**: 새로운 섹션은 기존의 '겨울방학 추천 도서', '어린이 도서 연구회' 섹션과 **동일한 UI 구조**를 유지해야 합니다.
- **컴포넌트 재사용**: `BookList`, `BookCard` 등 이미 검증된 공통 컴포넌트를 사용하여 개발 효율성과 사용자 경험의 일관성을 확보합니다.

### 모바일 큐레이션 레이아웃 및 터치 스와이프 인터랙션
- **가로 스크롤 카드 레이아웃(Horizontal Scroll)**: 모바일(가로폭 360px)에서 화면 높이를 아끼고 여러 큐레이션을 한눈에 훑어볼 수 있도록 큐레이션 도서 목록은 기본적으로 가로 스크롤(Flex wrap 대신 `overflow-x-auto`, `flex-nowrap`)이 가능한 형태로 구현한다.
- **가로 스크롤 지연 방지**: 터치 스와이프가 매끄럽게 동작하도록 CSS `scroll-behavior: smooth`와 `-webkit-overflow-scrolling: touch` 속성을 부여한다.
- **마지막 아이템 여백**: 가로 스크롤 시 마지막 도서 카드가 화면 우측 끝에 너무 달라붙지 않도록, 컨테이너 끝에 적절한 padding-right(최소 `16px`)를 확보해 모바일 터치 사용성을 높인다.

### 도서 태그 노출 및 중복 방지 규격 (4-Tag Rule)
- **상세 페이지 최대 4개 태그 노출**:
  - 도서 상세 페이지에서는 `[메타 태그 1개] + [핵심 큐레이션/주제 태그 최대 3개]` 구조로 최대 4개까지만 노출합니다.
  - 구체적인 학년 태그(`초등1~6학년`)가 존재하는 도서는 학년 태그를 맨 앞 메타 태그로 배치하며, 포괄적 연령 태그(예: `8~12세`)는 중복 방지를 위해 렌더링에서 배제합니다.
- **도서 카드 뱃지 정합성**:
  - 도서 카드(`BookItem.tsx`) 이미지 위 오버레이 뱃지에도 학년 태그가 있으면 연령 대신 학년을 우선 노출하고, 카드 하단 큐레이션 목록에서는 중복을 방지하기 위해 해당 학년 태그를 제외합니다.

### 구현 체크리스트
- [ ] **Data Fetching**: `lib/home-api.ts` 등에 해당 큐레이션을 위한 Fetch 함수 추가
- [ ] **Display Logic (Quality Control)**: 홈 화면 섹션의 경우, 사용자 경험을 위해 **최소 7권 이상의 도서**가 존재할 때만 섹션을 렌더링하도록 조건부 로직 추가
- [ ] **Component Update**: `HomePageClient.tsx`에 새로운 섹션 추가
- [ ] **Responsiveness**: 모바일/태블릿/데스크탑 환경에서의 스크롤 및 배치 확인
- [ ] **Link Routing**: "더보기" 클릭 시 해당 큐레이션 필터가 적용된 목록 페이지(`/books?curation=xxx`)로 이동
- [ ] **SEO 7대 파이프라인 동기화 (필수)**:
  1. `taxonomy.ts` (`ALL_TAXONOMY`, `VALID_AI_TAGS`)
  2. `layout.tsx` (메인 키워드 & 설명)
  3. `sitemap.ts` (`specialCurations` 및 하위 쿼리 경로)
  4. `collections/curation/[tag]/page.tsx` (`generateStaticParams`, `generateMetadata`, `isKnownCuration`, `SPECIAL_TAGS`, `ItemList` JSON-LD)
  5. `books/page.tsx` (`generateMetadata`, `SPECIAL_TAGS`, `ItemList` JSON-LD)
  6. `book/[id]/page.tsx` (도서 상세 특수 태그 배지, 메타데이터, `Book` JSON-LD)
  7. `npm run build` 빌드 및 정적 사전 생성 검증

#### [예시] 노출 품질 관리 로직 (Early return)
```tsx
function CurationSection({ title, books, ...props }) {
  // 7권 미만인 경우 섹션 자체를 노출하지 않음 (유저 경험 보장)
  if (books.length < 7) return null;
  
  return (
    <section>
      <h2>{title}</h2>
      <BookGrid books={books} />
    </section>
  );
}
```

### 큐레이션 리스트 노출 정렬 순서 규칙
- **시각적 연속성**: 유저가 메인 화면의 큐레이션 섹션에서 "더보기"를 눌러 전체 목록 페이지(`/books?curation=xxx`)로 전환했을 때의 연속적인 사용자 경험(UX)을 확보하기 위해 다음을 준수합니다.
- **홈 화면 노출 도서 상단 우선 고정**:
  - 홈 화면에 노출되었던 7권의 추천/큐레이션 도서가 목록 페이지에서도 항상 **최상단에 우선 노출**되도록 처리합니다. (`BookList.tsx`의 `shouldFetchRecommended`에 큐레이션 추가)
- **기본 정렬 순서(ㄱㄴㄷ 정렬)**:
  - 칼데콧 등 특별 테마 큐레이션의 경우, 유저가 정렬 필터를 변경하지 않은 기본 상태일 때 청구기호 대신 **제목(`title` 오름차순, 즉 ㄱㄴㄷ 순)**을 기본 정렬로 설정하여 홈 노출 순서와 일치시킵니다. (`supabase-client.ts`, `books-api-server.ts`에서 각 큐레이션에 맞는 기본 정렬 값을 분기 처리)

### 📅 주간 큐레이션 동기화 및 셔플 정책
- **홈페이지 동기화**: 홈페이지의 dynamic 큐레이션 섹션(2~4번째)은 7일 주기(목요일 기준)로 자동 갱신되며, 프론트엔드와 백엔드가 동일한 셔플 순서를 공유해야 합니다.
- **LCG 난수 및 Fisher-Yates 대칭 구현**:
  - 자바스크립트 오차와 시간대 편차 방지를 위해 UTC 타임스탬프 기준으로 Unix epoch 일수를 구한 후 시드(Seed)로 사용합니다.
  - 백엔드와 프론트엔드는 동일한 LCG(Linear Congruential Generator) 난수 식을 사용하며, 초기 LCG 연산에 32비트 비트 마스킹(`& 0xffffffff`)을 반드시 적용합니다.
  - Fisher-Yates 셔플 알고리즘을 이 시드 기반 LCG로 실행하여 두 환경에서 100% 동일한 순서의 큐레이션 테마(예: 1. 과학원리, 2. 사회성, 3. 감정조절)를 노출합니다.

### 🏷️ 큐레이션 태그 통합 및 7-Book Rule 검증 체계 (Tag Management)
- **파편화 태그 통합 (Taxonomy Consolidation)**: 수량이 1~2권에 불과한 세부 소형 태그(`명절`, `전통놀이` 등)는 상위 대표 태그(`우리문화` 등)로 1st 태그를 일괄 통합/병합(Merge)하여 데이터 밀도(30권 이상)와 7-Book Rule 통과율을 높입니다.
- **핀포인트 1st 태그 정밀 교정**: 태그 정확도를 손상시키지 않기 위해, 줄거리 정합성이 100% 검증된 2~3순위 태그 도서 1~2권만 1st 태그로 핀포인트 조정하여 7권 통과 기준으로 보강합니다.
- **시의성/시즌 맞춤 배치 (Seasonal Curation Alignment)**: 개학철(8월 하순: `#적응`), 추석 연휴(9월 하순: `#우리문화`, `#전래동화`, `#가족사랑`) 등 시즌 특수에 맞춰 주간 큐레이션 및 스레드 피드를 맞춤 배치합니다.
- **전후 4주(한 달 안팎) 중복 노출 완전 차단**: 주간 스케줄 재배치 시 임의의 주차를 기준으로 전후 4주(한 달) 범위 내에 동일 태그가 중복 노출되지 않도록 윈도우 중복 검증 알고리즘을 필수로 적용합니다.

### 🏷️ 특수 큐레이션 태그의 DB 분리 vs UI 통합 아키텍처 (Special Tag Architecture)
- **DB & 쿼리 레벨 (분리 유지)**:
  - `caldecott`, `어린이도서연구회`, `여름방학2026`, `겨울방학2026` 등 특수 태그는 일반 주제 태그(첫 번째 태그 정밀 매칭 `.eq`)와 달리 위치 무관 포함 쿼리(`ilike '%tag%'`)로 처리한다.
  - 태그 자동 재정렬(`reorder_curation_tags.py`) 시 특수 태그는 굶주림(Hunger) 카운트 관리에서 제외하며, 스레드 자동 발행(`threads.py`) 대상에서도 제외한다.
- **UI & 컴포넌트 레벨 (통합 및 중복 필터링)**:
  - UI 컴포넌트에서 특수 태그를 임의로 숨기지 않고(`HIDDEN_UI_TAGS = empty`) 일반 태그와 동일하게 표시한다.
  - `CurationSection`에 `sectionTag` prop을 전달하고 `BookItem`에 `excludeTag` prop을 적용하여, 홈 큐레이션 카드에서는 섹션 대표 태그 1개만 제외하고 나머지 부가 태그를 자연스럽게 노출한다.

### 🏷️ 청구기호 및 다중 도서관 동기화 (Call Number Sync)
- **메인 컬럼 동기화 필수**: 도서관별 청구기호를 `book_library_info`에 적재할 때, `childbook_items.pangyo_callno` 컬럼에도 판교도서관 청구기호(없을 시 타 도서관 대표 청구기호)를 함께 업데이트해야 목록 페이지(`/books?curation=xxx`) 및 SEO 페이지(`/collections/curation/[tag]`)에서 정상 노출됩니다.
- **사전 건강검진 실행**: 주간 스케줄 반영 전 반드시 `python3 backend/scripts/check_curation_health.py`를 실행하여 청구기호가 존재하는 유효 도서가 7권 이상인지 확인합니다.

### 🏷️ 홈 큐레이션-도서 목록 헤더 타이틀 정책 (Header Title Policy)
- **헤더 타이틀 이모티콘 배제**: 도서 리스트 상단 `PageHeader` 타이틀은 `ALL_TAXONOMY`의 `title` 속성을 매핑하되, 정규식을 통해 이모티콘(이모지)을 완전히 제거한 순수 텍스트(예: `스르륵 꿀잠 그림책`)로 일관되게 노출합니다.
- **교과서 수록도서 및 학년별 태그 분기**: `searchParams.get('tag')`를 확인하여 학년 태그(예: `초등1학년`)가 존재할 경우 `초등 1학년 교과서 수록도서`, 전체일 경우 `교과서 수록도서`로 이모티콘 없이 명확히 분기합니다.
- **인기 큐레이션 칩 바 동기화**: `POPULAR_CURATION_CHIPS`에 `📖 교과서`(`tag: '교과서수록'`) 칩을 포함하여 홈 주요 코너와 퀵 이동 칩 간 정합성을 유지합니다.

### 🏷️ 태그 정제 및 파싱 규약 (Tag Sanitization & Grade Tags)
- **DB 저장 불변식**: `curation_tag` 컬럼의 태그는 항상 `#`이 없는 순수 한글/영문 쉼표 구분자 포맷(예: `전래동화,옛이야기,권선징악`)으로 저장 및 적재합니다.
- **UI 파싱 SSOT**: UI 렌더링 시 `frontend/lib/utils/curation-filter.ts`의 `parseCurationTags()`, `formatCurationTag()`, `isGradeTag()`, `extractGradeTag()`를 유일한 단일 진실 공급원(SSOT)으로 사용합니다. `parseCurationTags()`는 `Set` 기반의 순서 유지 중복 제거를 지원하여 동일 태그 다중 노출을 원천 방어합니다.
- **학년 태그 표준 노출**: 초등 학년 태그(`초등1학년` ~ `초등6학년`)는 `TAG_DISPLAY_NAMES`를 통해 띄어쓰기가 적용된 `초등 N학년` 형태로 UI에 노출합니다.

### 🔗 큐레이션 "더보기" 링크 생성 단일 규격 (`getCurationMoreLink`)
- **수동 URL 조립 금지**: 컴포넌트마다 `URLSearchParams`를 수동 생성하면 `age`, `tag`, `sort` 파라미터가 유실되어 목록 진입 시 시각적 연속성이 깨집니다.
- **단일 함수 호출**: 모든 더보기 링크는 `getCurationMoreLink({ curation, age, tag, sort })`(`frontend/lib/utils/curation-link.ts`)를 호출하여 생성합니다.
  - **특수 큐레이션 (칼데콧, 방학, 도서연구회)**: 전체 도서 풀 노출을 위해 `age`, `tag` 파라미터를 배제하고 `/books?curation=...` 반환
  - **교과서 수록도서**: 학년 `tag`가 있을 때 `/books?curation=교과서수록&tag=...` 반환
  - **AI 주제 큐레이션**: 등록된 슬러그가 있을 때 `/collections/curation/[slug]?age=...&tag=...`, 없을 때 `/books?curation=...` 반환
  - **연령별 추천**: `/books?age=...&sort=popular` 반환
- **React Query 정렬 캐시 동기화**: `BookList.tsx`의 `queryKey`에 `sortFilter`를 필수로 포함하여, 인기순/신뢰도순 등 정렬 파라미터 변경 시 캐시 오염 없이 즉시 최신 데이터가 조회되도록 유지합니다.

## 4. 검증 및 배포 (Verification)
- **데이터 무결성 확인**: 이미지가 깨지지 않는지, ISBN이 정확한지 SQL 조회 및 UI 확인
- **청구기호 유효성 및 헬스체크**: `python3 backend/scripts/check_curation_health.py` 실행하여 전수 통과 확인
- **가독성 점검**: [디자인 팀장 페르소나](file:///Users/1004823/Desktop/kids_library/.agent/rules/design.md) 기준에 맞춰, 타이틀과 책 정보가 서가 환경(모바일)에서도 잘 보이는지 확인



