import { Metadata } from 'next'
import HomePageClient from '@/components/HomePageClient'

export const metadata: Metadata = {
  metadataBase: new URL("https://checkjari.com"),
  alternates: { canonical: '/' },
  title: "책자리 - 도서관 헛걸음 그만! 3초 만에 책 찾기",
  description: "아직도 도서관에서 헤매세요? 대출 가능 여부부터 위치까지 한눈에 확인!",
  keywords: "어린이 도서, 어린이 추천 책, 도서관, 어린이 도서관, 청구기호, 판교도서관",
  openGraph: {
    title: "책자리 - 도서관 헛걸음 그만! 3초 만에 책 찾기",
    description: "아직도 도서관에서 헤매세요? 대출 가능 여부부터 위치까지 한눈에 확인!",
    url: "https://checkjari.com",
    images: [
      {
        url: "/logo.png",
        width: 1200,
        height: 630,
        alt: "책자리 로고",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "책자리 - 도서관 헛걸음 그만! 3초 만에 책 찾기",
    description: "아직도 도서관에서 헤매세요? 대출 가능 여부부터 위치까지 한눈에 확인!",
    images: ["/logo.png"],
  },
};

export default function HomePage() {
  return <HomePageClient />
}
