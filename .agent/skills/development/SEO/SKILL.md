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

## 4. 체크리스트
- [ ] `Metadata` 정의 (Title, Description, Keywords)
- [ ] `Canonical URL` 설정 (중복 콘텐츠 방지)
- [ ] `Open Graph` 및 `Twitter Card` 설정
- [ ] `sitemap.ts` 경로 등록
- [ ] 중요 페이지 `JSON-LD` 주입
