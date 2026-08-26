import { Metadata } from 'next'
import HomePageClient from '@/components/HomePageClient'
import { getResearchCouncilBooks, getBooksByAge, getBooksByTag, getSummerBooks } from '@/lib/home-api'
import { getCaldecottBooks } from '@/lib/caldecott-api'
import { createClient } from '@/lib/supabase'
import { VALID_TAXONOMY, CurationTag } from '@/lib/constants/taxonomy'
import weeklySchedule from '../shared/weekly_schedule.json'

import { isSummerCurationActive } from '@/lib/utils/curation-filter'

export const revalidate = 3600; // 1시간 주기 ISR 캐시 활성화

export const metadata: Metadata = {
  metadataBase: new URL("https://checkjari.com"),
  alternates: { canonical: '/' },
  title: "내 주변 도서관 책 검색 & 그림책 대출 가능 여부 3초 조회",
  description: "도서관 가기 전 헛걸음 방지! 내 주변 도서관의 책 검색, 실시간 대출 가능 상태와 청구기호를 3초 만에 조회하세요. 연령 및 정서 발달에 딱 맞는 그림책 큐레이션도 제공합니다.",
  keywords: "어린이 도서 추천, 유아 그림책 큐레이션, 초등 필독서, 칼데콧 수상작, 어린이도서연구회, 연령별 추천도서, 책자리, 어린이 정서 교육, 아이 감정 발달, 상황별 그림책, 주변 도서관 책 검색, 도서관 대출",
  openGraph: {
    title: "내 주변 도서관 책 검색 & 그림책 대출 가능 여부 3초 조회 | 책자리",
    description: "도서관 가기 전 헛걸음 방지! 내 주변 도서관의 책 검색, 실시간 대출 가능 상태와 청구기호를 3초 만에 조회하세요. 연령 및 정서 발달에 딱 맞는 그림책 큐레이션도 제공합니다.",
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
    title: "내 주변 도서관 책 검색 & 그림책 대출 가능 여부 3초 조회 | 책자리",
    description: "도서관 가기 전 헛걸음 방지! 내 주변 도서관의 책 검색, 실시간 대출 가능 상태와 청구기호를 3초 만에 조회하세요. 연령 및 정서 발달에 딱 맞는 그림책 큐레이션도 제공합니다.",
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
  const [researchBooks, ageBooks, caldecottBooks, summerBooks, ...dynamicBooks] = await Promise.all([
    getResearchCouncilBooks(7, supabase, false),
    getBooksByAge(defaultAge, 7, supabase, false),
    getCaldecottBooks(supabase, false),
    isSummerCurationActive() ? getSummerBooks(7, supabase, false) : Promise.resolve([]),
    ...selectedTags.map(t => getBooksByTag(t.tag, 7, supabase, false))
  ])

  // HomePageClient에 전달할 동적 큐레이션 데이터 구성
  const dynamicCurations = selectedTags.map((tag, index) => ({
    subtitle: tag.subtitle,
    title: tag.title,
    tag: tag.tag,
    books: dynamicBooks[index]
  }))

  const jsonLd = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'WebSite',
        '@id': 'https://checkjari.com/#website',
        url: 'https://checkjari.com',
        name: '책자리',
        description: '내 주변 도서관 책 검색 및 연령별 그림책 큐레이션 서비스',
        inLanguage: 'ko-KR',
        potentialAction: {
          '@type': 'SearchAction',
          target: {
            '@type': 'EntryPoint',
            urlTemplate: 'https://checkjari.com/search?q={search_term_string}',
          },
          'query-input': 'required name=search_term_string',
        },
      },
      {
        '@type': 'Organization',
        '@id': 'https://checkjari.com/#organization',
        name: '책자리',
        url: 'https://checkjari.com',
        logo: {
          '@type': 'ImageObject',
          url: 'https://checkjari.com/logo.png',
          width: 512,
          height: 512,
        },
        sameAs: [
          'https://www.threads.net/@checkjari',
        ],
      },
    ],
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <HomePageClient
        initialCaldecottBooks={caldecottBooks.slice(0, 7)}
        initialResearchBooks={researchBooks}
        initialAgeBooks={ageBooks}
        initialSummerBooks={summerBooks}
        initialSelectedAge={defaultAge}
        dynamicCurations={dynamicCurations}
      />
    </>
  )
}
