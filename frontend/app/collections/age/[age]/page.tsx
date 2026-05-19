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
        title: '0-3세 영유아 그림책 추천 | 전집 고민 끝! 사서가 뽑은 베스트 - 책자리',
        description: '0~3세 아이의 두뇌 발달·감각 자극·정서 안정에 맞는 그림책을 전문 사서가 골랐어요. 지금 도서관에서 바로 만나보세요.',
        keywords: '0-3세 추천 도서, 영유아 그림책 추천, 아기 그림책, 돌 그림책, 베스트 영유아 도서, 사서 추천 도서, 북스타트'
    },
    '4-7': {
        title: '4-7세 유아 그림책 추천 | 유치원생 필독서 리스트 - 책자리',
        description: '4~7세 아이의 정서 발달·상상력·언어 성장에 맞는 그림책을 전문 사서가 골랐어요. 지금 도서관에서 바로 만나보세요.',
        keywords: '4-7세 추천 도서, 유아 그림책 추천, 유치원 책 추천, 인기 유아 도서, 사서 추천, 베스트 그림책'
    },
    '8-12': {
        title: '초등학생 필독서 추천 | 학년별 베스트셀러 한눈에 - 책자리',
        description: '8~12세 초등학생의 사고력·창의력·공감 능력을 키우는 책을 전문 사서가 엄선했어요. 지금 도서관에서 바로 만나보세요.',
        keywords: '초등학생 필독서, 초등 추천 도서, 초등 권장도서, 학년별 추천 도서, 사서 추천, 초등 베스트셀러, 인기 어린이 책'
    },
    'teen': {
        title: '청소년 필독서 추천 | 중고등학생이 진짜 읽는 책 - 책자리',
        description: '사춘기 자녀의 자아 탐색·세계관 형성을 돕는 책을 전문 사서가 골랐어요. 지금 도서관에서 바로 만나보세요.',
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
