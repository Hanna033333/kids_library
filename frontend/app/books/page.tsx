import HomeClient from "@/components/HomeClient";
import { Metadata } from 'next'

interface Props {
    searchParams: Promise<{ age?: string; curation?: string; category?: string; q?: string }>
}

export async function generateMetadata({ searchParams }: Props): Promise<Metadata> {
    const params = await searchParams
    const { age, curation, q } = params

    let title = '책자리 - 도서 검색'
    let description = '판교도서관의 도서를 검색하고 청구기호를 확인하세요.'
    let keywords = '어린이 도서, 도서 검색, 판교도서관'

    if (curation === '겨울방학') {
        title = '겨울방학 사서 추천 도서 | 책자리'
        description = '방학에 읽기 좋은 사서 추천 도서 목록입니다. 판교도서관 청구기호와 대출 가능 여부를 바로 확인하세요.'
        keywords = '겨울방학 추천도서, 사서 추천, 어린이 방학 책, 초등 필독서'
    } else if (curation === '어린이도서연구회') {
        title = '어린이 도서 연구회 추천 도서 | 책자리'
        description = '전문가가 엄선한 어린이 권장 도서 목록입니다.'
        keywords = '어린이 도서 연구회, 전문가 추천 도서, 권장도서'
    } else if (age) {
        if (age === '0-3') {
            title = '0-3세 추천 도서 (영유아) | 책자리'
            description = '0-3세 영유아를 위한 추천 그림책 목록입니다.'
        } else if (age === '4-7') {
            title = '4-7세 추천 도서 (유아) | 책자리'
            description = '4-7세 유아를 위한 창작 동화와 그림책 목록입니다.'
        } else if (age === '8-12') {
            title = '8-12세 추천 도서 (초등) | 책자리'
            description = '초등학생을 위한 교과 연계 및 필독서 목록입니다.'
        } else if (age === '13+') {
            title = '13세 이상 추천 도서 (청소년) | 책자리'
            description = '청소년을 위한 인문/교양 추천 도서 목록입니다.'
        }
    } else if (q) {
        title = `'${q}' 검색 결과 | 책자리`
        description = `'${q}'에 대한 도서 검색 결과입니다. 판교도서관 소장 여부를 확인하세요.`
    }

    return {
        title,
        description,
        keywords,
        openGraph: {
            title,
            description,
            type: 'website',
            url: `https://checkjari.com/books?${new URLSearchParams(params as any).toString()}`
        },
        twitter: {
            card: 'summary_large_image',
            title,
            description
        }
    }
}

export const dynamic = 'force-dynamic';

export default function BooksPage() {
    return <HomeClient />;
}
