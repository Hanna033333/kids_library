import { Metadata } from 'next'
import HomePageClient from '@/components/HomePageClient'
import { getWinterBooks, getResearchCouncilBooks, getBooksByAge, getBooksByTag } from '@/lib/home-api'
import { getCaldecottBooks } from '@/lib/caldecott-api'
import { createClient } from '@/lib/supabase-server'
import { VALID_TAXONOMY } from '@/lib/constants/taxonomy'

export const dynamic = 'force-dynamic';

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

  // 3일 단위 시드 계산 (날짜 기반 결정적 랜덤)
  const now = new Date()
  const daysSinceEpoch = Math.floor(now.getTime() / (1000 * 60 * 60 * 24))
  const seed = Math.floor(daysSinceEpoch / 3)

  // LCG(선형합동법) 기반 시드 난수 생성기 - seed=0 포함 모든 구간에서 균등한 분포 보장
  let lcgState = seed * 1664525 + 1013904223
  const seededRandom = () => {
    lcgState = (lcgState * 1664525 + 1013904223) & 0xffffffff
    return (lcgState >>> 0) / 0x100000000
  }

  // VALID_TAXONOMY 배열 셔플 (Fisher-Yates)
  const shuffledTags = [...VALID_TAXONOMY]
  for (let i = shuffledTags.length - 1; i > 0; i--) {
    const j = Math.floor(seededRandom() * (i + 1))
    ;[shuffledTags[i], shuffledTags[j]] = [shuffledTags[j], shuffledTags[i]]
  }

  // 상위 3개 태그 선택
  const selectedTags = shuffledTags.slice(0, 3)

  // 서버 사이드 병렬 데이터 페칭
  const [researchBooks, ageBooks, caldecottBooks, ...dynamicBooks] = await Promise.all([
    getResearchCouncilBooks(7, supabase),
    getBooksByAge(defaultAge, 7, supabase),
    getCaldecottBooks(supabase),
    ...selectedTags.map(t => getBooksByTag(t.tag, 7, supabase))
  ])

  // HomePageClient에 전달할 동적 큐레이션 데이터 구성
  const dynamicCurations = selectedTags.map((tag, index) => ({
    subtitle: tag.subtitle,
    title: tag.title,
    tag: tag.tag,
    books: dynamicBooks[index]
  }))

  return <HomePageClient
    initialCaldecottBooks={caldecottBooks.slice(0, 7)}
    initialResearchBooks={researchBooks}
    initialAgeBooks={ageBooks}
    initialSelectedAge={defaultAge}
    dynamicCurations={dynamicCurations}
  />
}
