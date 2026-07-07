import { Metadata } from 'next'
import HomePageClient from '@/components/HomePageClient'
import { getResearchCouncilBooks, getBooksByAge, getBooksByTag } from '@/lib/home-api'
import { getCaldecottBooks } from '@/lib/caldecott-api'
import { createClient } from '@/lib/supabase'
import { VALID_TAXONOMY, CurationTag } from '@/lib/constants/taxonomy'
import weeklySchedule from '../shared/weekly_schedule.json'

export const revalidate = 3600; // 1시간 주기 ISR 캐시 활성화

export const metadata: Metadata = {
  metadataBase: new URL("https://checkjari.com"),
  alternates: { canonical: '/' },
  title: "주변 도서관 그림책 대출 + 연령별 큐레이션 | 책자리",
  description: "우리 동네 도서관에 이 책이 있을까? 전국 도서관 대출 상태와 청구기호를 실시간으로 확인하고, 연령/정서별 엄선된 그림책 큐레이션을 만나보세요!",
  keywords: "어린이 도서 추천, 유아 그림책 큐레이션, 초등 필독서, 칼데콧 수상작, 어린이도서연구회, 연령별 추천도서, 책자리, 어린이 정서 교육, 아이 감정 발달, 상황별 그림책, 주변 도서관 책 검색, 도서관 대출",
  openGraph: {
    title: "주변 도서관 그림책 대출 + 연령별 큐레이션 | 책자리",
    description: "우리 동네 도서관에 이 책이 있을까? 전국 도서관 대출 상태와 청구기호를 실시간으로 확인하고, 연령/정서별 엄선된 그림책 큐레이션을 만나보세요!",
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
    title: "주변 도서관 그림책 대출 + 연령별 큐레이션 | 책자리",
    description: "우리 동네 도서관에 이 책이 있을까? 전국 도서관 대출 상태와 청구기호를 실시간으로 확인하고, 연령/정서별 엄선된 그림책 큐레이션을 만나보세요!",
    images: ["/logo.png"],
  },
};

export default async function HomePage() {
  const supabase = createClient()
  const defaultAge = '4-7'

  // KST (UTC+9) 날짜 구하기
  const now = new Date()
  const kstOffset = 9 * 60 * 60 * 1000
  const kstNow = new Date(now.getTime() + kstOffset)
  const dateStr = kstNow.toISOString().split('T')[0] // "YYYY-MM-DD"

  let selectedTags: CurationTag[];
  const matched = weeklySchedule.find(item => dateStr >= item.start && dateStr <= item.end);
  if (matched) {
    selectedTags = matched.curations as any[];
  } else {
    // 7일 단위 시드 계산 (UTC Unix timestamp 기반 일수 계산으로 백엔드와 100% 동기화)
    const daysSinceEpoch = Math.floor(now.getTime() / (1000 * 60 * 60 * 24))
    const seed = Math.floor(daysSinceEpoch / 7)

    // LCG(선형합동법) 기반 시드 난수 생성기
    let lcgState = (seed * 1664525 + 1013904223) & 0xffffffff
    const seededRandom = () => {
      lcgState = (lcgState * 1664525 + 1013904223) & 0xffffffff
      return (lcgState >>> 0) / 0x100000000
    }

    // 이미 검증된 weeklySchedule 세트 중 하나를 대칭적으로 선택 (FE/BE 100% 정합성 및 가용성 보장)
    const targetIdx = Math.floor(seededRandom() * weeklySchedule.length)
    const safeIdx = Math.max(0, Math.min(targetIdx, weeklySchedule.length - 1))
    selectedTags = weeklySchedule[safeIdx].curations as any[]
  }

  // 서버 사이드 병렬 데이터 페칭 (홈 화면에서는 도서관 소장 정보 조인을 생략하여 TTFB 단축)
  const [researchBooks, ageBooks, caldecottBooks, ...dynamicBooks] = await Promise.all([
    getResearchCouncilBooks(7, supabase, false),
    getBooksByAge(defaultAge, 7, supabase, false),
    getCaldecottBooks(supabase, false),
    ...selectedTags.map(t => getBooksByTag(t.tag, 7, supabase, false))
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
