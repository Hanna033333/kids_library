import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import AgeCollectionClient from './AgeCollectionClient'

interface Props {
    params: Promise<{ age: string }>
}

const ageMetadata: Record<string, { title: string; description: string; keywords: string }> = {
    '0-3': {
        title: '0-3세 영유아 그림책 추천 | 전집 고민 끝! 사서가 뽑은 베스트 - 책자리',
        description: '전집 고민 끝! 0-3세 아기 발달에 딱 맞는 그림책을 도서관에서 바로 대출하세요. 사서가 엄선한 베스트 영유아 도서 리스트를 지금 확인하세요.',
        keywords: '0-3세 추천 도서, 영유아 그림책 추천, 아기 그림책, 돌 그림책, 베스트 영유아 도서, 사서 추천 도서, 북스타트'
    },
    '4-7': {
        title: '4-7세 유아 그림책 추천 | 유치원생 필독서 리스트 - 책자리',
        description: '우리 아이 첫 독서 습관! 4-7세 유치원생에게 딱 맞는 인기 그림책을 도서관에서 만나보세요. 전문가가 추천하는 유아 필독서 리스트입니다.',
        keywords: '4-7세 추천 도서, 유아 그림책 추천, 유치원 책 추천, 인기 유아 도서, 사서 추천, 베스트 그림책'
    },
    '8-12': {
        title: '초등학생 필독서 추천 | 학년별 베스트셀러 한눈에 - 책자리',
        description: '초등학생 자녀를 위한 필독서! 학년별 맞춤 추천 도서를 도서관에서 바로 찾아보세요. 사서와 교사가 엄선한 초등 베스트셀러 리스트입니다.',
        keywords: '초등학생 필독서, 초등 추천 도서, 초등 권장도서, 학년별 추천 도서, 사서 추천, 초등 베스트셀러, 인기 어린이 책'
    },
    'teen': {
        title: '청소년 필독서 추천 | 중고등학생이 진짜 읽는 책 - 책자리',
        description: '중고등학생을 위한 필독서! 사춘기 자녀에게 꼭 필요한 책을 도서관에서 만나보세요. 전문가가 추천하는 청소년 베스트 도서 리스트입니다.',
        keywords: '청소년 필독서, 중학생 추천 도서, 고등학생 권장도서, 청소년 베스트셀러, 사서 추천, 인기 청소년 책'
    }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { age } = await params
    if (!ageMetadata[age]) {
        return { title: '책자리 - 연령별 추천 도서' }
    }
    const meta = ageMetadata[age]
    return {
        metadataBase: new URL("https://checkjari.com"),
        alternates: { canonical: `/collections/age/${age}` },
        title: meta.title,
        description: meta.description,
        keywords: meta.keywords,
        authors: [{ name: "책자리" }],
        openGraph: {
            title: meta.title,
            description: meta.description,
            url: `https://checkjari.com/collections/age/${age}`,
            siteName: "책자리",
            locale: "ko_KR",
            type: "website",
            images: [{ url: "/logo.png", width: 1200, height: 630, alt: `${age}세 추천 도서 - 책자리` }]
        },
        twitter: {
            card: "summary_large_image",
            title: meta.title,
            description: meta.description,
            images: ["/logo.png"]
        },
        robots: { index: true, follow: true, googleBot: { index: true, follow: true } }
    }
}

import { getBooksFromServer } from '@/lib/books-api-server'
import { createClient } from '@/lib/supabase-server'

// ... (previous imports)

export default async function AgeCollectionPage({ params }: Props) {
    const { age } = await params
    if (!['0-3', '4-7', '8-12', 'teen'].includes(age)) notFound()

    const supabase = createClient()
    const { data: initialBooks } = await getBooksFromServer({
        page: 1,
        limit: 24,
        filters: { age, sort: 'pangyo_callno' },
        client: supabase
    })

    return <AgeCollectionClient age={age} initialBooks={initialBooks} />
}
