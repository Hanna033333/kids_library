import HomeClient from "@/components/HomeClient";
import { Metadata } from 'next'

interface Props {
    searchParams: { age?: string; curation?: string; category?: string; q?: string }
}

export async function generateMetadata({ searchParams }: Props): Promise<Metadata> {
    const { age, curation, q } = searchParams

    let title = '책자리 - 도서 검색'
    let description = '판교도서관의 도서를 검색하고 청구기호를 확인하세요.'
    let keywords = '어린이 도서, 도서 검색, 판교도서관'

    if (curation === 'winter-vacation' || curation === '겨울방학') {
        title = '스마트폰만 보는 아이, 방학 때 뭐 읽힐까요?'
        description = '사서가 직접 뽑았다! 실패 없는 겨울방학 추천도서 리스트를 도서관에서 바로 대출하세요. 초등학생 필독서부터 인기 베스트까지 한눈에 확인하세요.'
        keywords = '겨울방학 독서 숙제, 초등 겨울방학 추천도서, 문해력 향상 도서, 독서록 쓰기 좋은 책, 학년별 추천 도서, 사서 추천'
    } else if (curation === 'research-council' || curation === '어린이도서연구회') {
        title = "전문가가 보증하는 '찐' 필독서 모음"
        description = '엄마표 독서 고민 끝! 어린이 도서 연구회가 엄선한 필독서를 도서관에서 바로 대출하세요. 전문가 추천 베스트 어린이 책 리스트를 지금 확인하세요.'
        keywords = '어린이 도서 연구회, 전문가 추천 도서, 사서 추천, 어린이 필독서, 베스트 어린이 책, 권장도서'
    } else if (age) {
        if (age === '0-3') {
            title = '우리 아이 나이에 딱! 0-3세 맞춤 도서'
            description = '전집 고민 그만! 0-3세 발달 단계에 딱 맞는 도서관 책 추천'
        } else if (age === '4-7') {
            title = '우리 아이 나이에 딱! 4-7세 맞춤 도서'
            description = '전집 고민 그만! 4-7세 발달 단계에 딱 맞는 도서관 책 추천'
        } else if (age === '8-12') {
            title = '우리 아이 나이에 딱! 8-12세 맞춤 도서'
            description = '전집 고민 그만! 8-12세 발달 단계에 딱 맞는 도서관 책 추천'
        } else if (age === 'teen') {
            title = '우리 아이 나이에 딱! 청소년 맞춤 도서'
            description = '전집 고민 그만! 청소년 발달 단계에 딱 맞는 도서관 책 추천'
        }
    } else if (q) {
        title = `'${q}' - 도서관에 있을까?`
        description = `헛걸음 NO! 대출 가능 여부와 위치를 바로 확인하세요`
    }

    return {
        title,
        description,
        keywords,
        openGraph: {
            title,
            description,
            type: 'website',
            url: `https://checkjari.com/books?${new URLSearchParams(searchParams as any).toString()}`
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
