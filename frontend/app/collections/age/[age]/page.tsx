import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import AgeCollectionClient from './AgeCollectionClient'

interface Props {
    params: Promise<{ age: string }>
}

const ageDisplayNames: Record<string, string> = {
    '0-3': '0~3세', '4-7': '4~7세', '8-12': '8~12세', 'teen': '13세 이상'
}

const ageMetadata: Record<string, { title: string; description: string; keywords: string }> = {
    '0-3': {
        title: '0-3세 영유아 그림책 추천 & 주변 도서관 책 검색 가능 여부 3초 확인',
        description: '0~3세 아기 발달과 감각 자극에 딱 맞는 전문 사서 엄선 그림책 큐레이션! 내 주변 도서관에서 실시간 책 검색, 대출 상태와 청구기호를 확인하고 대출하세요.',
        keywords: '주변 도서관 책 검색, 0-3세 추천 도서, 영유아 그림책 추천, 아기 그림책, 돌 그림책, 베스트 영유아 도서, 사서 추천 도서, 북스타트'
    },
    '4-7': {
        title: '4-7세 유아 그림책 추천 & 내 주변 도서관 책 검색 및 대출 확인',
        description: '4~7세 유치원생 발달 단계에 맞춘 실패 없는 추천 그림책 리스트! 내 근처 도서관에 책이 있는지 실시간 검색하고 헛걸음 없이 바로 대출해 보세요.',
        keywords: '주변 도서관 책 검색, 4-7세 추천 도서, 유아 그림책 추천, 유치원 책 추천, 인기 유아 도서, 사서 추천, 베스트 그림책'
    },
    '8-12': {
        title: '초등학생 필독서 추천 & 주변 도서관 책 검색 및 실시간 대출 상태',
        description: '8~12세 초등 학년별 문해력 향상 필수 도서 목록! 내 주변 공공도서관에 소장되어 있는지 실시간으로 책 검색하고 청구기호를 조회해 보세요.',
        keywords: '주변 도서관 책 검색, 초등학생 필독서, 초등 추천 도서, 초등 권장도서, 학년별 추천 도서, 사서 추천, 초등 베스트셀러, 인기 어린이 책'
    },
    'teen': {
        title: '청소년 필독서 추천 & 내 주변 도서관 책 검색 가능 여부 3초 확인',
        description: '사춘기 자녀의 자아 탐색·세계관 형성을 돕는 책을 전문 사서가 골랐어요. 내 주변 도서관 실시간 대출 가능 상태와 청구기호를 즉시 확인하세요.',
        keywords: '주변 도서관 책 검색, 청소년 필독서, 중학생 추천 도서, 고등학생 권장도서, 청소년 베스트셀러, 사서 추천, 인기 청소년 책'
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
import { getBooksByAge } from '@/lib/home-api'

export default async function AgeCollectionPage({ params }: Props) {
    const { age } = await params
    if (!['0-3', '4-7', '8-12', 'teen'].includes(age)) notFound()

    const supabase = createClient()

    // 서버에서 두 데이터를 병렬 패치 → SSR 단계에서 올바른 순서 확정
    const [{ data: rawBooks }, recommendedBooks] = await Promise.all([
        getBooksFromServer({ page: 1, limit: 24, filters: { age, sort: 'pangyo_callno' }, client: supabase }),
        getBooksByAge(age, 7)
    ])

    // 연령별 캔메넘 7권을 앞으로, 나머지는 포함되지 않은 쿽(ㄱㄴㄷ)순 유지
    const recIds = new Set(recommendedBooks.map((b: { id: number }) => b.id))
    const restBooks = (rawBooks ?? []).filter(b => !recIds.has(b.id))
    const initialBooks = [...recommendedBooks, ...restBooks]

    // ✅ 서버 컴포넌트에서 JSON-LD 생성
    const jsonLd = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        name: `${ageDisplayNames[age] ?? age} 추천 도서 - 책자리`,
        description: ageMetadata[age]?.description,
        url: `https://checkjari.com/collections/age/${age}`,
        numberOfItems: initialBooks?.length ?? 0,
        itemListElement: (initialBooks ?? []).slice(0, 10).map((book, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            item: {
                '@type': 'Book',
                name: book.title,
                ...(book.author ? { author: { '@type': 'Person', name: book.author } } : {}),
                ...(book.isbn ? { isbn: book.isbn } : {}),
                ...(book.image_url ? { image: book.image_url } : {}),
                url: `https://checkjari.com/book/${book.id}`,
            }
        }))
    }

    return (
        <>
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />
            <AgeCollectionClient age={age} initialBooks={initialBooks} />
        </>
    )
}
