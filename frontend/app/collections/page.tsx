import { Metadata } from 'next';
import CollectionsPageClient from './CollectionsPageClient';

export const revalidate = 3600;

export const metadata: Metadata = {
  title: '50+가지 상황별 도서 큐레이션 테마 모아보기',
  description:
    '아이의 연령, 정서, 상황(잠자리, 자존감, 사회성, 과학, 모험 등)에 맞춘 50여 가지 그림책 큐레이션 테마를 둘러보세요.',
  keywords: [
    '그림책 큐레이션',
    '어린이 도서 추천',
    '잠자리 그림책',
    '사회성 그림책',
    '자존감 그림책',
    '칼데콧 수상작',
    '어린이도서연구회',
    '책자리',
  ],
  openGraph: {
    title: '50+가지 상황별 도서 큐레이션 테마 모아보기 | 책자리',
    description:
      '아이의 연령과 정서적 상황에 꼭 맞는 엄선된 그림책 큐레이션 테마 모음집입니다.',
    url: 'https://www.checkjari.com/collections',
  },
};

export default function CollectionsPage() {
  return <CollectionsPageClient />;
}
