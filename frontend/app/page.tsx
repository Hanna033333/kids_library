import { Metadata } from 'next'
import HomePageClient from '@/components/HomePageClient'
import { getWinterBooks, getResearchCouncilBooks, getBooksByAge } from '@/lib/home-api'
import { getCaldecottBooks } from '@/lib/caldecott-api'
import { createClient } from '@/lib/supabase-server'

export const metadata: Metadata = {
  metadataBase: new URL("https://checkjari.com"),
  alternates: { canonical: '/' },
  title: "책자리 - 도서관 청구기호/위치 3초 확인 (내 도서관 설정)",
  description: "도서관 책 찾기 필수템. 우리 아이 나이 맞춤 도서와 내 동네 도서관 검색 결과를 로그인 한 번으로 더 편리하게 확인하세요.",
  keywords: "도서관, 어린이 도서관, 도서관 도서검색, 청구기호 찾기, 어린이 도서, 책자리, 판교도서관, 새 학기 추천도서, 초등 필독서",
  openGraph: {
    title: "책자리 - 도서관 청구기호/위치 3초 확인 (내 도서관 설정)",
    description: "도서관 책 찾기 필수템. 우리 아이 나이 맞춤 도서와 내 동네 도서관 검색 결과를 로그인 한 번으로 더 편리하게 확인하세요.",
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
    title: "책자리 - 도서관 청구기호/위치 3초 확인 (내 도서관 설정)",
    description: "도서관 책 찾기 필수템. 우리 아이 나이 맞춤 도서와 내 동네 도서관 검색 결과를 로그인 한 번으로 더 편리하게 확인하세요.",
    images: ["/logo.png"],
  },
};

export default async function HomePage() {
  const supabase = createClient()
  const defaultAge = '4-7'

  // 서버 사이드 병렬 데이터 페칭
  const [/* winterBooks */, researchBooks, ageBooks, caldecottBooks] = await Promise.all([
    // getWinterBooks(7, supabase),
    Promise.resolve([]), // Placeholder for winterBooks
    getResearchCouncilBooks(7, supabase),
    getBooksByAge(defaultAge, 7, supabase),
    getCaldecottBooks(supabase)
  ])

  return <HomePageClient
    // initialWinterBooks={winterBooks}
    initialCaldecottBooks={caldecottBooks.slice(0, 7)}
    initialResearchBooks={researchBooks}
    initialAgeBooks={ageBooks}
    initialSelectedAge={defaultAge}
  />
}
