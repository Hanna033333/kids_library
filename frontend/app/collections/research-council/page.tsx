import { Metadata } from 'next'
import ResearchCouncilClient from './ResearchCouncilClient'

export const metadata: Metadata = {
    metadataBase: new URL("https://checkjari.com"),
    alternates: { canonical: "/collections/research-council" },
    title: "어린이 도서 연구회 추천 도서 | 전문가 선정 필독서 - 책자리",
    description: "어린이 도서 전문가가 엄선한 필독서! 믿고 보는 사서 추천 도서를 도서관에서 바로 대출하세요. 검증된 베스트 어린이 책 리스트를 지금 확인하세요.",
    keywords: "어린이 도서 연구회, 사서 추천 도서, 전문가 추천, 어린이 필독서, 베스트 어린이 책, 권장도서, 인기 어린이 도서",
    authors: [{ name: "책자리" }],
    openGraph: {
        title: "어린이 도서 연구회 추천 도서 | 전문가 선정 필독서",
        description: "어린이 도서 전문가가 엄선한 필독서! 믿고 보는 사서 추천 도서를 도서관에서 바로 대출하세요.",
        url: "https://checkjari.com/collections/research-council",
        siteName: "책자리",
        locale: "ko_KR",
        type: "website",
        images: [{ url: "/logo.png", width: 1200, height: 630, alt: "어린이 도서 연구회 추천 도서 - 책자리" }]
    },
    twitter: {
        card: "summary_large_image",
        title: "어린이 도서 연구회 추천 도서 | 전문가 선정 필독서",
        description: "어린이 도서 전문가가 엄선한 필독서! 믿고 보는 사서 추천 도서를 도서관에서 바로 대출하세요.",
        images: ["/logo.png"]
    },
    robots: { index: true, follow: true, googleBot: { index: true, follow: true } }
}

export const dynamic = 'force-dynamic'

export default function ResearchCouncilPage() {
    return <ResearchCouncilClient />
}
