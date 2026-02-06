import { Metadata } from 'next'
import HomePageClient from '@/components/HomePageClient'
import { getWinterBooks, getResearchCouncilBooks, getBooksByAge } from '@/lib/home-api'
import { getCaldecottBooks } from '@/lib/caldecott-api'
import { createClient } from '@/lib/supabase-server'

export const metadata: Metadata = {
  metadataBase: new URL("https://checkjari.com"),
  alternates: { canonical: '/' },
  title: "책자리 - 도서관 청구기호 찾기, 3초면 끝 (로그인X)",
  description: "도서관 책 찾기 필수템. 로그인 없이 청구기호와 대출 가능 여부를 3초 만에 확인하세요. 키오스크 줄 서지 마세요!",
  keywords: "도서관, 어린이 도서관, 도서관 도서검색, 청구기호 찾기, 어린이 도서, 책자리, 판교도서관",
  openGraph: {
    title: "책자리 - 도서관 청구기호 찾기, 3초면 끝 (로그인X)",
    description: "도서관 책 찾기 필수템. 로그인 없이 청구기호와 대출 가능 여부를 3초 만에 확인하세요. 키오스크 줄 서지 마세요!",
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
    title: "책자리 - 도서관 청구기호 찾기, 3초면 끝 (로그인X)",
    description: "도서관 책 찾기 필수템. 로그인 없이 청구기호와 대출 가능 여부를 3초 만에 확인하세요. 키오스크 줄 서지 마세요!",
    images: ["/logo.png"],
  },
};

export default async function HomePage() {
  const supabase = createClient()
  const defaultAge = '4-7'

  // 서버 사이드 병렬 데이터 페칭
  const [winterBooks, researchBooks, ageBooks, caldecottBooks] = await Promise.all([
    getWinterBooks(7, supabase),
    getResearchCouncilBooks(7, supabase),
    getBooksByAge(defaultAge, 7, supabase),
    getCaldecottBooks(supabase)
  ])

  return <HomePageClient
    initialWinterBooks={winterBooks}
    initialCaldecottBooks={caldecottBooks.slice(0, 7)}
    initialResearchBooks={researchBooks}
    initialAgeBooks={ageBooks}
    initialSelectedAge={defaultAge}
  />
}
