---
name: SEO Optimization
description: Next.js(App Router) 환경의 검색 엔진 최적화(SEO) 표준 가이드
---

# SEO 최적화 가이드

본 문서는 프로젝트 내 새로운 페이지 추가 시 준수해야 할 SEO 표준 절차를 정의한다.

## 1. 메타데이터 (Metadata)

Next.js의 `Metadata` API를 사용하여 각 페이지의 제목, 설명, 키워드 및 Open Graph 태그를 설정한다.

### 정적 메타데이터
`layout.tsx` 또는 정적 `page.tsx`에 정의한다.
```typescript
export const metadata: Metadata = {
  title: "페이지 제목",
  description: "페이지 설명",
  openGraph: {
    title: "공유 시 제목",
    description: "공유 시 설명",
    images: ["/og-image.png"],
  },
};
```

### 동적 메타데이터
쿼리 파라미터나 동적 라우트에 따라 `generateMetadata`를 사용한다.
```typescript
export async function generateMetadata({ searchParams }: Props): Promise<Metadata> {
  const { q } = searchParams;
  return {
    title: q ? `${q} - 도서 검색` : "도서관 책 찾기",
    // ...
  };
}
```

## 2. 사이트맵 (Sitemap)

새로운 주요 서비스 경로가 추가되면 `frontend/app/sitemap.ts`에 해당 경로를 등록해야 한다.

- **정적 경로**: `routes` 배열에 직접 추가
- **동적 경로**: DB에서 데이터를 조회하여 `routes.push()`로 추가

```typescript
// frontend/app/sitemap.ts 예시
const routes: MetadataRoute.Sitemap = [
    { url: `${baseUrl}/caldecott`, lastModified: new Date(), priority: 0.9 },
];
```

## 3. 구조화된 데이터 (JSON-LD)

검색 엔진이 페이지의 성격(도서, 목록 등)을 더 잘 이해할 수 있도록 JSON-LD를 주입한다.

### 도서 목록 (ItemList)
큐레이션 페이지나 검색 결과 페이지에서 사용한다.
```tsx
const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    itemListElement: books.map((book, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        item: {
            '@type': 'Book',
            name: book.title,
            // ...
        },
    })),
};

return (
    <>
        <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <Component />
    </>
);
```

### 참고: 수상작/큐레이션 전용 (Caldecott 예시)
특정 기획성 페이지(예: `/caldecott`)의 경우, 검색 결과 노출도를 높이기 위해 다음과 같이 상세 메타데이터와 JSON-LD를 구성한다.

**메타데이터 설정:**
```typescript
export const metadata: Metadata = {
    title: "칼데콧 수상작 (2000-2026) - 책자리",
    description: "2000년부터 2026년까지 칼데콧 메달을 수상한 세계 최고의 어린이 그림책 목록입니다. 판교도서관 청구기호와 대출 정보를 확인하세요.",
    keywords: "칼데콧상, Caldecott Medal, 어린이 그림책, 수상작, 추천 도서, 판교도서관",
    openGraph: {
        title: "칼데콧 수상작 (2000-2026) - 책자리",
        description: "2000년부터 2026년까지 칼데콧 메달을 수상한 세계 최고의 어린이 그림책 목록입니다.",
        url: "https://checkjari.com/caldecott",
        images: [{ url: "/logo.png", width: 1200, height: 630, alt: "책자리 - 칼데콧 수상작" }],
    },
};
```

**ItemList 기반 JSON-LD:**
```typescript
const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    itemListElement: books.map((book, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        item: {
            '@type': 'Book',
            name: book.title,
            author: { '@type': 'Person', name: book.author },
            isbn: book.isbn,
            image: book.image_url,
            url: `https://checkjari.com/book/${book.id}`,
        },
    })),
};
```

## 4. 체크리스트
- [ ] `Metadata` 정의 (Title, Description, Keywords)
- [ ] `Canonical URL` 설정 (중복 콘텐츠 방지)
- [ ] `Open Graph` 및 `Twitter Card` 설정
- [ ] `sitemap.ts` 경로 등록
- [ ] 중요 페이지 `JSON-LD` 주입
- [ ] `Viewport Meta Tag` 설정 확인 (모바일 배율 지원)
- [ ] 모바일 친화성(Mobile Usability) 검증 (모바일 기기 뷰포트 오버플로우 방지)
- [ ] 데스크톱과 모바일의 SEO 데이터(Metadata, JSON-LD) 동일성 확인

---

## 5. 모바일 우선 인덱싱 (Mobile-First Indexing) 대응
구글 등의 주요 검색 엔진은 모바일 버전의 페이지를 기준으로 색인과 노출 순위를 매깁니다. 이에 대응하기 위해 다음 요소를 준수합니다.
- **Viewport Meta Tag 필수 지정**: 모바일 뷰포트 배율 설정이 제대로 되어 있는지 프론트엔드 최상위 `layout.tsx`에 meta 설정을 검토한다.
  - 예시: `viewport: "width=device-width, initial-scale=1.0"`
- **모바일 Usability (사용성) 최적화**: 모바일 봇이 페이지를 긁어갈 때 터치 영역이 겹치거나 텍스트가 뷰포트 너비를 넘어가 모바일 친화성 에러가 생기지 않도록, 모바일 우선 CSS 설계를 바탕으로 레이아웃을 작성한다.
- **콘텐츠 및 구조 정합성**: 데스크톱과 모바일 버전의 웹페이지에서 동일한 양의 마크업 데이터(메타데이터, JSON-LD, 텍스트)를 제공하여 모바일 기기에서의 검색 불이익이 생기지 않도록 한다.

---

## 6. 도서 및 큐레이션 섹션 추가 시 7대 필수 동기화 절차 (Mandatory Sync Pipeline)

신규 추천 도서나 큐레이션 섹션(예: 교과서 수록도서, 특별 테마 큐레이션 등)을 추가할 때는 UI 컴포넌트 추가에 그치지 않고 반드시 아래 **7대 SEO 파일 동기화**를 일괄 수행해야 합니다.

```
[1. taxonomy.ts] ➔ [2. layout.tsx] ➔ [3. sitemap.ts] ➔ [4. collections/curation/page.tsx]
       ➔ [5. books/page.tsx] ➔ [6. book/[id]/page.tsx] ➔ [7. npm run build 검증]
```

### 파일별 수정 가이드
1. **`frontend/lib/constants/taxonomy.ts`**:
   - `ALL_TAXONOMY` 배열에 신규 테마의 `{ id, subtitle, title, tag, slug }` 추가
   - `VALID_AI_TAGS` 배열에 신규 한글 태그명 추가 (단축 링크 `/c/[tag]` 및 맵퍼 지원)
2. **`frontend/app/layout.tsx`**:
   - `metadata.description` 및 `metadata.keywords`에 신규 큐레이션 핵심 타겟 키워드 보강
3. **`frontend/app/sitemap.ts`**:
   - `specialCurations` 배열에 신규 슬러그 및 한글 태그명 추가
   - 세부 학년별/분류별 쿼리 경로(예: `/books?curation=교과서수록&tag=초등1학년`)가 있는 경우 사이트맵 routes에 함께 등록
4. **`frontend/app/collections/curation/[tag]/page.tsx`**:
   - `generateStaticParams()`의 `specialCurations`에 슬러그 추가 (SSG 사전 빌드)
   - `generateMetadata()`에 해당 큐레이션 전용 Title, Description, Keywords 분기 추가
   - `CurationPage` 컴포넌트의 `isKnownCuration`, `SPECIAL_TAGS` 및 `ItemList` JSON-LD 쿼리에 매핑 로직 추가
5. **`frontend/app/books/page.tsx`**:
   - `generateMetadata()`에 `curation` 및 `tag` 조건 분기 추가
   - `BooksPage` 컴포넌트의 `isKnownCuration`, `SPECIAL_TAGS` 및 `ItemList` JSON-LD 쿼리 동기화
6. **`frontend/app/book/[id]/page.tsx`**:
   - 도서의 `curation_tag`에 따른 특수 배지/테마 판별(`isTextbook`, `isCaldecott` 등)
   - Title 접두사(`[초등 교과서 수록]`, `[칼데콧 수상작]` 등), Description, Keywords 및 `Book` JSON-LD의 `genre`/`description` 최적화
7. **빌드 검증**:
   - `npm run build`를 실행하여 SSG 정적 페이지 생성(190+ 페이지) 및 메타데이터 타입 오류 여부를 최종 확인

