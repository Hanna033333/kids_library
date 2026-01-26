import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import AgeCollectionClient from './AgeCollectionClient'

interface Props {
    params: Promise<{ age: string }>
}

const ageMetadata: Record<string, { title: string; description: string; keywords: string }> = {
    '0-3': {
        title: '우리 아이 나이에 딱! 0-3세 맞춤 도서',
        description: '전집 고민 그만! 0-3세 발달 단계에 딱 맞는 도서관 책 추천',
        keywords: '0-3세 추천 도서, 영유아 그림책, 돌 그림책, 판교도서관, 청구기호, 어린이 도서'
    },
    '4-7': {
        title: '우리 아이 나이에 딱! 4-7세 맞춤 도서',
        description: '전집 고민 그만! 4-7세 발달 단계에 딱 맞는 도서관 책 추천',
        keywords: '4-7세 추천 도서, 유아 그림책, 유치원 책, 판교도서관, 청구기호, 어린이 도서'
    },
    '8-12': {
        title: '우리 아이 나이에 딱! 8-12세 맞춤 도서',
        description: '전집 고민 그만! 8-12세 발달 단계에 딱 맞는 도서관 책 추천',
        keywords: '8-12세 추천 도서, 초등학생 필독서, 초등 권장도서, 판교도서관, 청구기호, 어린이 도서'
    },
    '13+': {
        title: '우리 아이 나이에 딱! 13세+ 맞춤 도서',
        description: '전집 고민 그만! 13세 이상 발달 단계에 딱 맞는 도서관 책 추천',
        keywords: '13세 이상 추천 도서, 청소년 필독서, 중학생 권장도서, 판교도서관, 청구기호, 청소년 도서'
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

export default async function AgeCollectionPage({ params }: Props) {
    const { age } = await params
    if (!['0-3', '4-7', '8-12', '13+'].includes(age)) notFound()
    return <AgeCollectionClient age={age} />
}
