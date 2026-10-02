import { Metadata } from 'next';
import CollectionsPageClient from './CollectionsPageClient';
import { VALID_TAXONOMY } from '@/lib/constants/taxonomy';

export const revalidate = 3600;

export const metadata: Metadata = {
  metadataBase: new URL('https://checkjari.com'),
  alternates: { canonical: '/collections' },
  title: '50+ 전문 테마 큐레이션 | 우리 아이 상황별 맞춤 그림책 처방전',
  description:
    '잠투정, 훈육, 사회성, 자존감, 과학 호기심 등 아이의 발달과 상황에 맞춘 50여 가지 전문 그림책 큐레이션 테마를 둘러보고 도서관 대출 현황을 즉시 확인하세요.',
  keywords: [
    '그림책 큐레이션',
    '어린이 도서 추천',
    '상황별 그림책',
    '잠자리 그림책',
    '사회성 그림책',
    '자존감 그림책',
    '초등 교과서 수록도서',
    '칼데콧 수상작',
    '어린이도서연구회',
    '책자리',
  ],
  authors: [{ name: '책자리' }],
  openGraph: {
    title: '50+ 전문 테마 큐레이션 | 우리 아이 상황별 맞춤 그림책 처방전 - 책자리',
    description:
      '아이의 연령과 정서적 상황(잠투정, 훈육, 사회성 등)에 꼭 맞는 50여 가지 엄선된 그림책 큐레이션 테마 모음집입니다.',
    url: 'https://checkjari.com/collections',
    siteName: '책자리',
    locale: 'ko_KR',
    type: 'website',
    images: [
      {
        url: '/logo.png',
        width: 1200,
        height: 630,
        alt: '50+ 전문 테마 큐레이션 - 책자리',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: '50+ 전문 테마 큐레이션 | 우리 아이 상황별 맞춤 그림책 처방전 - 책자리',
    description:
      '아이의 연령과 정서적 상황에 꼭 맞는 50여 가지 엄선된 그림책 큐레이션 테마 모음집입니다.',
    images: ['/logo.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
};

export default function CollectionsPage() {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: '50+ 전문 테마 큐레이션 - 책자리',
    description: '아이의 연령, 정서, 상황에 맞춘 50여 가지 전문 그림책 큐레이션 테마 모음',
    url: 'https://checkjari.com/collections',
    mainEntity: {
      '@type': 'ItemList',
      numberOfItems: VALID_TAXONOMY.length,
      itemListElement: VALID_TAXONOMY.map((item, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        item: {
          '@type': 'Collection',
          name: `${item.tag} - ${item.title}`,
          description: item.subtitle,
          url: `https://checkjari.com/collections/curation/${item.slug}`,
        },
      })),
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <CollectionsPageClient />
    </>
  );
}
