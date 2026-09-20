'use client'

import { useState, useEffect, useRef, useMemo, useTransition } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { ChevronRight, BookOpen } from 'lucide-react'
import { Book } from '@/lib/types'
import { getTextbookBooks } from '@/lib/home-api'
import { useAuth } from '@/context/AuthContext'
import { PageLoader } from '@/components/ui/PageLoader'
import { sendGAEvent } from '@/lib/analytics'
import { getOptimizedImageUrl, isValidCoverImage } from '@/lib/utils/image'
import { getCurationMoreLink } from '@/lib/utils/curation-link'

export interface GradeTab {
  id: string
  label: string
  tag: string
  displayName: string
}

export const TEXTBOOK_GRADE_TABS: GradeTab[] = [
  { id: 'all', label: '전체', tag: 'all', displayName: '전체' },
  { id: 'grade-1', label: '초등 1학년', tag: '초등1학년', displayName: '1학년' },
  { id: 'grade-2', label: '초등 2학년', tag: '초등2학년', displayName: '2학년' },
  { id: 'grade-3', label: '초등 3학년', tag: '초등3학년', displayName: '3학년' },
  { id: 'grade-4', label: '초등 4학년', tag: '초등4학년', displayName: '4학년' },
  { id: 'grade-5', label: '초등 5학년', tag: '초등5학년', displayName: '5학년' },
  { id: 'grade-6', label: '초등 6학년', tag: '초등6학년', displayName: '6학년' },
]

interface TextbookCurationShowcaseProps {
  initialTab?: string
  initialBooks?: Book[]
  bgColor?: string
}

/**
 * 도서에서 표시할 태그 추출 (제목 상단 배치용)
 */
function getDisplayTag(book: Book, activeTabTag: string): string {
  if (book.curation_tag) {
    const rawTags = book.curation_tag
      .split(',')
      .map(t => t.trim().replace(/^#/, ''))
      .filter(t => t && t !== '교과서수록')

    // 학년 관련 태그가 있으면 우선 표시
    const gradeTag = rawTags.find(t => t.includes('초등') || t.includes('학년'))
    if (gradeTag) {
      return gradeTag.startsWith('#') ? gradeTag : `#${gradeTag}`
    }

    if (rawTags.length > 0) {
      return rawTags[0].startsWith('#') ? rawTags[0] : `#${rawTags[0]}`
    }
  }

  if (activeTabTag && activeTabTag !== 'all') {
    return `#${activeTabTag.replace(/^#/, '')}`
  }

  return '#초등필독'
}

export default function TextbookCurationShowcase({
  initialTab = 'all',
  initialBooks,
  bgColor = 'bg-white'
}: TextbookCurationShowcaseProps) {
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

  const currentTab = TEXTBOOK_GRADE_TABS.find(tab => tab.id === activeTabId) || TEXTBOOK_GRADE_TABS[0]

  // 탭 변경 시 데이터 로드 (캐시 우선, userId만 의존)
  useEffect(() => {
    let isCancelled = false

    if (cacheRef.current[currentTab.id]) {
      setLoading(false)
      return
    }

    setLoading(true)
    getTextbookBooks(currentTab.tag === 'all' ? undefined : currentTab.tag, 8, undefined, !!userId)
      .then(books => {
        if (!isCancelled) {
          setCache(prev => ({ ...prev, [currentTab.id]: books }))
          setLoading(false)
        }
      })
      .catch(err => {
        console.error('Error loading textbook books:', err)
        if (!isCancelled) setLoading(false)
      })

    return () => {
      isCancelled = true
    }
  }, [currentTab.id, currentTab.tag, userId])

  const handleTabClick = (tab: GradeTab) => {
    if (tab.id === activeTabId) return

    sendGAEvent('click_textbook_grade_tab', {
      tab_id: tab.id,
      grade_tag: tab.tag
    })

    startTransition(() => {
      setActiveTabId(tab.id)
    })
  }

  const currentBooks = useMemo(
    () => (cache[currentTab.id] || []).filter(b => isValidCoverImage(b.image_url)),
    [cache, currentTab.id]
  )

  // 2단 배열을 위해 2권씩 묶기 (Column Pairs, useMemo 적용)
  const bookPairs = useMemo(() => {
    const pairs: Book[][] = []
    for (let i = 0; i < currentBooks.length; i += 2) {
      pairs.push(currentBooks.slice(i, i + 2))
    }
    return pairs
  }, [currentBooks])

  // 전체보기 링크 URL
  const viewMoreUrl = getCurationMoreLink({
    curation: '교과서수록',
    tag: currentTab.tag === 'all' ? undefined : currentTab.tag,
  })

  return (
    <section className={`py-8 px-4 ${bgColor}`}>
      <div className="max-w-[1200px] mx-auto">
        {/* 섹션 헤더 (2단 타이틀만 깔끔하게 노출) */}
        <div className="mb-6 px-2">
          <span className="text-[13px] font-semibold text-gray-500 tracking-tight">
            초등 국어 수업에 실제로 실린
          </span>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight leading-tight mt-1">
            📖 교과서 수록도서
          </h2>
        </div>

        {/* 학년별 가로 스크롤 탭 바 */}
        <div className="overflow-x-auto scrollbar-hide -mx-4 px-6 mb-6">
          <div className="flex items-center gap-2 pb-1">
            {TEXTBOOK_GRADE_TABS.map(tab => {
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
          </div>
        </div>

        {/* 2단 도서 가로 스크롤 영역 */}
        {loading ? (
          <div className="h-[220px] flex items-center justify-center mx-2">
            <PageLoader />
          </div>
        ) : bookPairs.length > 0 ? (
          <div>
            <div className="overflow-x-auto scrollbar-hide -mx-4 px-6">
              <div className="flex gap-3 pb-3">
                {bookPairs.map((pair, colIndex) => (
                  <div
                    key={`col-${colIndex}`}
                    className={`flex flex-col gap-3 w-[310px] sm:w-[370px] lg:w-[455px] shrink-0 ${
                      colIndex === bookPairs.length - 1 ? 'mr-4' : ''
                    }`}
                  >
                    {pair.map((book) => {
                      const displayTag = getDisplayTag(book, currentTab.tag)
                      const coverSrc = getOptimizedImageUrl(book.image_url, 'list')
                      return (
                        <Link
                          key={book.id}
                          href={`/book/${book.id}`}
                          onClick={() => {
                            sendGAEvent('click_textbook_book_card', {
                              book_id: book.id,
                              title: book.title,
                              tab_id: currentTab.id
                            })
                          }}
                          className="flex items-center p-3.5 bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] active:scale-[0.98] transition-all group"
                        >
                          {/* 표지 썸네일 (130% 확대) */}
                          <div className="relative w-[110px] h-[150px] sm:w-[120px] sm:h-[164px] lg:w-[125px] lg:h-[172px] shrink-0 rounded-xl overflow-hidden bg-gray-100 shadow-sm flex items-center justify-center">
                            {coverSrc ? (
                              <Image
                                src={coverSrc}
                                alt={book.title}
                                fill
                                sizes="(max-width: 640px) 120px, 150px"
                                className="object-cover"
                                loading="lazy"
                              />
                            ) : (
                              <div className="flex items-center justify-center w-full h-full text-gray-300">
                                <BookOpen className="w-8 h-8 opacity-20" />
                              </div>
                            )}
                          </div>

                          {/* 우측 정보: 태그(상단) -> 제목(중단) -> 저자/출판사(하단) */}
                          <div className="flex flex-col justify-center min-w-0 flex-1 pl-4 pr-1.5 py-1">
                            {/* 1. 태그 ('전체' 탭 선택 시에만 학년 식별용 태그 표시) */}
                            {currentTab.tag === 'all' && displayTag && (
                              <span className="text-[12.5px] sm:text-[13px] font-medium text-gray-500 truncate mb-1">
                                {displayTag}
                              </span>
                            )}

                            {/* 2. 제목 (원본 도서 제목 렌더링) */}
                            <h3 className="text-[14.5px] sm:text-[15.5px] font-bold text-gray-900 line-clamp-2 leading-snug">
                              {book.title}
                            </h3>

                            {/* 3. 저자 */}
                            {book.author && (
                              <p className="text-[12.5px] sm:text-[13px] text-gray-500 line-clamp-1 mt-1.5">
                                {book.author}
                              </p>
                            )}
                          </div>
                        </Link>
                      )
                    })}
                  </div>
                ))}
              </div>
            </div>

            {/* 현재 학년 도서 전체보기 링크 (디자인 시스템 표준 미니멀 텍스트 링크) */}
            <div className="mt-3 text-center">
              <Link
                href={viewMoreUrl}
                onClick={() => sendGAEvent('click_view_more', { section: `textbook_${currentTab.tag}` })}
                className="inline-flex items-center gap-1 text-[13.5px] font-bold text-gray-500 active:text-gray-900 transition-colors py-1 group cursor-pointer"
              >
                <span>{currentTab.label} 교과서 수록도서 전체보기</span>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </Link>
            </div>
          </div>
        ) : (
          <div className="h-[180px] flex flex-col items-center justify-center text-gray-400 text-sm">
            <p>해당 학년의 교과서 수록도서를 불러올 수 없습니다.</p>
          </div>
        )}
      </div>
    </section>
  )
}
