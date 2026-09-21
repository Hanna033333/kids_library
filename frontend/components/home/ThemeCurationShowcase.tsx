'use client'

import { useState, useEffect, useRef, useTransition } from 'react'
import Link from 'next/link'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Book } from '@/lib/types'
import { getBooksByTag } from '@/lib/home-api'
import { useAuth } from '@/context/AuthContext'
import { PageLoader } from '@/components/ui/PageLoader'
import BookCard from './BookCard'
import { sendGAEvent } from '@/lib/analytics'
import { isValidCoverImage } from '@/lib/utils/image'
import { getCurationMoreLink } from '@/lib/utils/curation-link'

export interface ThemeTab {
  id: string
  label: string
  tag: string
  subtitle: string
}

export const POPULAR_THEME_TABS: ThemeTab[] = [
  { id: 'sleep', label: '잠자리', tag: '잠자리', subtitle: '밤마다 안 자려는 우리 아이에게' },
  { id: 'self-esteem', label: '자존감', tag: '자존감', subtitle: '기 죽지 않고 단단하게 자라도록' },
  { id: 'social', label: '첫 사회성', tag: '사회성', subtitle: '친구랑 더 재미있게 놀고 싶을 때' },
  { id: 'school', label: '기관적응', tag: '적응', subtitle: '새로운 환경에서도 씩씩하고 즐겁게' },
  { id: 'emotion', label: '감정·마음', tag: '감정조절', subtitle: '폭발하는 감정을 다스리는 지혜' },
  { id: 'dinosaurs', label: '공룡', tag: '공룡', subtitle: '수억 년 전 지구를 지배한 주인공' },
  { id: 'nature', label: '자연·생태', tag: '자연관찰', subtitle: '신비한 숲속과 들판의 비밀' },
  { id: 'art', label: '예술·창의', tag: '예술감성', subtitle: '아름다움을 느끼는 눈과 마음을 길러요' },
  { id: 'science', label: '호기심·과학', tag: '과학원리', subtitle: '세상의 원리를 깨우치는 재미' },
  { id: 'family', label: '가족사랑', tag: '가족사랑', subtitle: '세상에서 가장 따뜻한 품' },
]

interface ThemeCurationShowcaseProps {
  initialTab?: string
  initialBooks?: Book[]
  bgColor?: string
}

export default function ThemeCurationShowcase({
  initialTab = 'sleep',
  initialBooks,
  bgColor = 'bg-muted-bg'
}: ThemeCurationShowcaseProps) {
  const { user } = useAuth()
  const userId = user?.id
  const [activeTabId, setActiveTabId] = useState<string>(initialTab)
  const [cache, setCache] = useState<Record<string, Book[]>>(() => {
    if (initialBooks && initialBooks.length > 0) {
      return { [initialTab]: initialBooks }
    }
    return {}
  })
  const cacheRef = useRef(cache)
  cacheRef.current = cache

  const [loading, setLoading] = useState<boolean>(!initialBooks || initialBooks.length === 0)
  const [, startTransition] = useTransition()
  const sliderRef = useRef<HTMLDivElement>(null)

  const currentTab = POPULAR_THEME_TABS.find(tab => tab.id === activeTabId) || POPULAR_THEME_TABS[0]

  // 탭 변경 시 데이터 로드 (캐시 우선, user?.id만 의존)
  useEffect(() => {
    let isCancelled = false

    if (cacheRef.current[currentTab.id]) {
      setLoading(false)
      if (sliderRef.current) {
        sliderRef.current.scrollTo({ left: 0, behavior: 'smooth' })
      }
      return
    }

    setLoading(true)
    getBooksByTag(currentTab.tag, 7, undefined, !!userId)
      .then(books => {
        if (!isCancelled) {
          setCache(prev => ({ ...prev, [currentTab.id]: books }))
          setLoading(false)
          if (sliderRef.current) {
            sliderRef.current.scrollTo({ left: 0, behavior: 'smooth' })
          }
        }
      })
      .catch(err => {
        console.error('Error loading tab books:', err)
        if (!isCancelled) setLoading(false)
      })

    return () => {
      isCancelled = true
    }
  }, [currentTab.id, currentTab.tag, userId])

  const handleTabClick = (tab: ThemeTab) => {
    if (tab.id === activeTabId) return

    sendGAEvent('click_theme_showcase_tab', {
      tab_id: tab.id,
      tab_tag: tab.tag
    })

    startTransition(() => {
      setActiveTabId(tab.id)
    })
  }

  // PC용 좌우 스크롤 제어
  const scrollSlider = (direction: 'left' | 'right') => {
    if (!sliderRef.current) return
    const scrollAmount = 450
    sliderRef.current.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth'
    })
  }

  const currentBooks = (cache[currentTab.id] || []).filter(b => isValidCoverImage(b.image_url))

  return (
    <section className={`py-8 px-4 ${bgColor}`}>
      <div className="max-w-[1200px] mx-auto">
        {/* 섹션 헤더 (2단 타이틀만 깔끔하게 노출) */}
        <div className="mb-6 px-2">
          <span className="text-[13px] font-semibold text-gray-500 tracking-tight">
            아이의 마음과 호기심을 채우는
          </span>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight leading-tight mt-1">
            ✨ 50+ 전문 테마 큐레이션
          </h2>
        </div>

        {/* 밀리의 서재 스타일 가로 스크롤 탭 바 (+ 50개 테마 더보기 칩 포함) */}
        <div className="overflow-x-auto scrollbar-hide -mx-4 mb-6">
          <div className="flex items-center gap-2 pb-1 px-6">
            {POPULAR_THEME_TABS.map(tab => {
              const isActive = tab.id === activeTabId
              return (
                <button
                  key={tab.id}
                  onClick={() => handleTabClick(tab)}
                  className={`shrink-0 px-4 py-2 rounded-full text-[14px] transition-all cursor-pointer ${
                    isActive
                      ? 'bg-brand-primary text-white font-bold shadow-sm active:scale-95'
                      : 'bg-white text-gray-700 font-medium border border-gray-200/80 active:bg-gray-100 active:scale-95'
                  }`}
                >
                  {tab.label}
                </button>
              )
            })}

            {/* 전체 테마 더보기 '>' 아이콘 버튼 (최소 48x48px 터치 규격) */}
            <Link
              href="/collections"
              onClick={() => sendGAEvent('click_theme_showcase_more_chip')}
              className="shrink-0 w-12 h-12 rounded-full bg-white border border-gray-200/80 flex items-center justify-center text-gray-400 active:text-gray-900 active:bg-gray-100 transition-all cursor-pointer active:scale-95 shadow-sm"
              aria-label="전체 테마 더보기"
            >
              <ChevronRight className="w-5 h-5" />
            </Link>
          </div>
        </div>

        {/* 도서 슬라이더 영역 */}
        {loading ? (
          <div className="h-[280px] flex items-center justify-center mx-2">
            <PageLoader />
          </div>
        ) : currentBooks.length > 0 ? (
          <div>
            <div className="relative group/slider">
              {/* PC 데스크톱 좌측 스크롤 버튼 */}
              <button
                onClick={() => scrollSlider('left')}
                className="hidden sm:flex absolute -left-4 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-white/90 shadow-md border border-gray-200 items-center justify-center text-gray-700 active:scale-95 cursor-pointer"
                aria-label="이전 도서 보기"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              {/* 슬라이더 컨테이너 */}
              <div
                ref={sliderRef}
                className="overflow-x-auto scrollbar-hide -mx-4 scroll-smooth"
              >
                <div className="flex gap-4 pb-4 items-stretch px-6">
                  {currentBooks.map((book) => (
                    <div
                      key={book.id}
                      className="flex-shrink-0 w-[165px] sm:w-[190px]"
                    >
                      <BookCard
                        book={book}
                        excludeTag={currentTab.tag}
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* PC 데스크톱 우측 스크롤 버튼 */}
              <button
                onClick={() => scrollSlider('right')}
                className="hidden sm:flex absolute -right-4 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-white/90 shadow-md border border-gray-200 items-center justify-center text-gray-700 active:scale-95 cursor-pointer"
                aria-label="다음 도서 보기"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>

            {/* 책 목록 하단: 디자인 시스템 표준 미니멀 텍스트 링크 */}
            <div className="mt-3 text-center">
              <Link
                href={getCurationMoreLink({ curation: currentTab.tag })}
                onClick={() => sendGAEvent('click_theme_showcase_bottom_cta', { section: currentTab.tag })}
                className="inline-flex items-center gap-1 text-[13.5px] font-bold text-gray-500 active:text-gray-900 transition-colors py-1 group cursor-pointer"
              >
                <span>{currentTab.label} 관련 도서 전체보기</span>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </Link>
            </div>
          </div>
        ) : (
          <div className="h-[200px] flex flex-col items-center justify-center text-gray-400 text-sm">
            <p>도서를 불러올 수 없습니다.</p>
          </div>
        )}
      </div>
    </section>
  )
}

