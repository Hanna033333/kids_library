import HomeClient from "@/components/HomeClient";
import { Metadata } from 'next'

interface Props {
    searchParams: Promise<{ age?: string; curation?: string; category?: string; q?: string }>
}

export async function generateMetadata({ searchParams }: Props): Promise<Metadata> {
    const params = await searchParams
    const { age, curation } = params
    let canonicalUrl = '/books'
    if (age && ['0-3', '4-7', '8-12', '13+'].includes(age)) canonicalUrl = `/collections/age/${age}`
    else if (curation === '겨울방학') canonicalUrl = '/collections/winter-vacation'
    else if (curation === '어린이도서연구회') canonicalUrl = '/collections/research-council'
    return {
        title: '모든 어린이 도서 목록 - 책자리',
        description: '책자리의 모든 어린이 도서를 연령별, 카테고리별로 찾아보세요.',
        alternates: { canonical: canonicalUrl }
    }
}

export const dynamic = 'force-dynamic';

export default function BooksPage() {
    return <HomeClient />;
}
