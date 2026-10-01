'use client'

import React, { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { ChevronLeft, ChevronRight, Pause, Play } from 'lucide-react'
import { sendGAEvent } from '@/lib/analytics'

export interface BannerItem {
  id: string;
  badge?: string;
  titleLines: [string, string];
  subtitle: string;
  href: string;
  slug: string;
  coverImage?: string;
  multiCovers?: string[];
  bgColor: string;
  glowColor: string;
  titleColor: string;
  subColor: string;
  badgeClass: string;
}

export const SPOTLIGHT_BANNERS: BannerItem[] = [
  {
    id: 'prescription',
    badge: '50+ 전문 테마 큐레이션',
    titleLines: ['우리 아이 맞춤 책', '상황별 50+ 처방전'],
    subtitle: '잠투정, 훈육, 사회성... 우리 아이 맞춤 큐레이션',
    href: '/collections',
    slug: 'collections',
    multiCovers: [
      'https://image.aladin.co.kr/product/49/78/cover500/8901044870_3.jpg',
      'https://image.aladin.co.kr/product/11467/53/cover500/8936427296_1.jpg',
      'https://image.aladin.co.kr/product/8232/52/cover500/k322434954_1.jpg',
      'https://image.aladin.co.kr/product/13514/88/cover500/8952786483_1.jpg',
      'https://image.aladin.co.kr/product/7848/68/cover500/k252434524_2.jpg',
      'https://image.aladin.co.kr/product/30077/82/cover500/k812839374_2.jpg',
      'https://image.aladin.co.kr/product/25151/14/cover500/8954674631_2.jpg',
      'https://image.aladin.co.kr/product/37564/79/cover500/k712032523_1.jpg',
    ],
    // MSF Blue (Primary): #6DD0F0
    bgColor: 'bg-[#6DD0F0]',
    glowColor: 'bg-sky-100/40',
    titleColor: 'text-gray-950',
    subColor: 'text-gray-900 font-semibold',
    badgeClass: 'bg-black/10 text-gray-950 border-black/15 font-bold',
  },
  {
    id: 'textbook',
    badge: '2022 개정 교육과정',
    titleLines: ['초등 교과서 수록도서', '학년별 필수 필독서'],
    subtitle: '1~6학년 국어 교과서에 실린 필독서로 문해력 쑥쑥',
    href: '/collections/curation/textbook',
    slug: 'textbook',
    coverImage: 'https://image.aladin.co.kr/product/30077/82/cover500/k812839374_2.jpg',
    // MSF Green (Primary): #00B487
    bgColor: 'bg-[#00B487]',
    glowColor: 'bg-emerald-200/30',
    titleColor: 'text-white',
    subColor: 'text-white/95 font-medium',
    badgeClass: 'bg-black/20 text-white border-white/25 font-bold',
  },
  {
    id: 'library',
    badge: '도서관 헛걸음 방지',
    titleLines: ['도서관 가기 전 3초', '지금 대출 가능할까?'],
    subtitle: '자주 가는 도서관의 실시간 대출 상태와 청구기호 즉시 조회',
    href: '/my-library',
    slug: 'my-library',
    coverImage: 'https://image.aladin.co.kr/product/7848/68/cover500/k252434524_2.jpg',
    // 책자리 메인 브랜드 컬러: #F59E0B
    bgColor: 'bg-[#F59E0B]',
    glowColor: 'bg-amber-200/35',
    titleColor: 'text-white',
    subColor: 'text-white/95 font-medium',
    badgeClass: 'bg-black/20 text-white border-white/25 font-bold',
  },
]

export default function SpotlightBanner() {
  const [activeBannerIndex, setActiveBannerIndex] = useState<number>(0)
  const [isPaused, setIsPaused] = useState<boolean>(false)
  const touchStartX = useRef<number | null>(null)

  // 5초 자동 롤링 타이머
  useEffect(() => {
    if (isPaused) return
    const timer = setInterval(() => {
      setActiveBannerIndex((prev) => (prev + 1) % SPOTLIGHT_BANNERS.length)
    }, 5000)
    return () => clearInterval(timer)
  }, [isPaused])

  const handlePrevBanner = (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    setActiveBannerIndex((prev) =>
      prev === 0 ? SPOTLIGHT_BANNERS.length - 1 : prev - 1
    )
  }

  const handleNextBanner = (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    setActiveBannerIndex((prev) => (prev + 1) % SPOTLIGHT_BANNERS.length)
  }

  const togglePause = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsPaused((prev) => !prev)
  }

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX
  }

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (touchStartX.current === null) return
    const touchEndX = e.changedTouches[0].clientX
    const diff = touchStartX.current - touchEndX
    if (diff > 40) {
      handleNextBanner()
    } else if (diff < -40) {
      handlePrevBanner()
    }
    touchStartX.current = null
  }

  const currentBanner = SPOTLIGHT_BANNERS[activeBannerIndex]

  return (
    <section className="w-full bg-white select-none">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6 pt-2 pb-3.5">
        <div
          className="relative group overflow-hidden rounded-2xl sm:rounded-3xl shadow-lg border-0"
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
        >
          <div
            className={`w-full ${currentBanner.bgColor} relative`}
          >
            {/* 은은한 배경 광원 효과 */}
            <div
              className={`absolute -right-10 -top-10 w-96 h-96 rounded-full ${currentBanner.glowColor} blur-3xl pointer-events-none`}
            />

            <Link
              href={currentBanner.href}
              onClick={() =>
                sendGAEvent('click_spotlight_banner', {
                  banner_id: currentBanner.id,
                  banner_slug: currentBanner.slug,
                  banner_title: currentBanner.titleLines.join(' '),
                  index: activeBannerIndex,
                })
              }
              className="relative block w-full h-[235px] sm:h-[285px] md:h-[315px] flex items-center px-5 sm:px-12 md:px-16"
            >
              {/* 배너 콘텐츠 레이아웃 (좌우 분할 가로형) */}
              <div className="w-full flex items-center justify-between">
                {/* 좌측: 뱃지 & 2줄 굵은 헤드라인 & 서브카피 */}
                <div className="relative z-10 max-w-[60%] sm:max-w-[58%] md:max-w-[54%] min-w-0 pr-2">
                  {currentBanner.badge && (
                    <div className={`inline-flex items-center px-2.5 py-0.5 sm:px-3 sm:py-1 rounded-md backdrop-blur-xs text-[11px] sm:text-xs font-bold border mb-2 sm:mb-3 ${currentBanner.badgeClass}`}>
                      {currentBanner.badge}
                    </div>
                  )}
                  <h2 className={`text-xl sm:text-2xl md:text-[32px] font-black leading-[1.3] md:leading-[1.32] tracking-tight ${currentBanner.titleColor} break-keep`}>
                    <span className="block whitespace-nowrap">{currentBanner.titleLines[0]}</span>
                    <span className="block whitespace-nowrap">{currentBanner.titleLines[1]}</span>
                  </h2>
                  <p className={`text-xs sm:text-sm md:text-base ${currentBanner.subColor} font-medium mt-2 sm:mt-3 leading-relaxed break-keep line-clamp-2`}>
                    {currentBanner.subtitle}
                  </p>
                </div>

                {/* 우측 비주얼: 다중 도서 그리드 or 큼직한 단일 도서 */}
                {currentBanner.multiCovers ? (
                  /* 2행 x 4열 다중 도서 그리드 쇼케이스 (총 8권) */
                  <div className="relative z-10 shrink-0 flex items-center justify-end pointer-events-none max-w-[40%] sm:max-w-[45%] md:max-w-[50%] overflow-hidden py-2 pr-1 sm:pr-4 md:pr-6">
                    <div className="grid grid-rows-2 grid-flow-col gap-1.5 sm:gap-2 md:gap-2.5 auto-cols-max">
                      {currentBanner.multiCovers.map((cover, idx) => (
                        <div
                          key={idx}
                          className={`relative w-[42px] h-[60px] sm:w-[68px] sm:h-[96px] md:w-[84px] md:h-[118px] rounded-sm sm:rounded-md overflow-hidden shadow-[0_8px_20px_rgba(0,0,0,0.3)] border border-white/40 bg-white/20 transition-transform duration-300 ${
                            idx >= 6 ? 'hidden sm:block' : ''
                          }`}
                        >
                          <Image
                            src={cover}
                            alt=""
                            fill
                            sizes="(max-width: 640px) 50px, 90px"
                            className="object-cover"
                            unoptimized
                          />
                          <div className="absolute inset-0 bg-gradient-to-tr from-black/15 via-transparent to-white/15 pointer-events-none" />
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  /* 입체 양장본 단일 도서 표지 쇼케이스 (비율 보존 & 3D 회전) */
                  <div className="absolute right-4 sm:right-10 md:right-16 top-1/2 -translate-y-1/2 pointer-events-none z-10">
                    <div className="relative w-[115px] sm:w-[155px] md:w-[180px] aspect-[1/1.4] rounded-r-md rounded-l-xs sm:rounded-r-lg sm:rounded-l-xs overflow-hidden shadow-[0_16px_36px_rgba(0,0,0,0.35),0_4px_12px_rgba(0,0,0,0.2)] border border-white/30 -rotate-3 sm:-rotate-4 transition-all duration-500 group-hover:scale-105 group-hover:-rotate-1">
                      <Image
                        src={currentBanner.coverImage || ''}
                        alt=""
                        fill
                        sizes="(max-width: 640px) 130px, 200px"
                        className="object-cover"
                        priority
                        unoptimized
                      />
                      {/* 책등(Book Spine) 입체 음영 효과 */}
                      <div className="absolute inset-y-0 left-0 w-2.5 sm:w-3.5 bg-gradient-to-r from-black/35 via-black/10 to-transparent pointer-events-none" />
                      {/* 표지 광택 하이라이트 */}
                      <div className="absolute inset-0 bg-gradient-to-tr from-black/10 via-transparent to-white/25 pointer-events-none" />
                    </div>
                  </div>
                )}
              </div>
            </Link>

            {/* 우측 하단 컨트롤러 (원형 일시정지 + < N / M > 알약형 컨트롤러) */}
            <div className="absolute bottom-3.5 right-3.5 sm:bottom-4 sm:right-6 z-20 flex items-center gap-1.5 sm:gap-2">
              <button
                onClick={togglePause}
                aria-label={isPaused ? '배너 재생' : '배너 일시정지'}
                className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-black/40 hover:bg-black/60 active:bg-black/80 backdrop-blur-md text-white flex items-center justify-center border border-white/15 shadow-sm transition-all cursor-pointer outline-none focus:outline-none focus-visible:outline-none ring-0"
              >
                {isPaused ? (
                  <Play className="w-2.5 h-2.5 sm:w-3 sm:h-3 fill-white text-white ml-0.5" />
                ) : (
                  <Pause className="w-2.5 h-2.5 sm:w-3 sm:h-3 fill-white text-white" />
                )}
              </button>

              <div className="inline-flex items-center px-1 sm:px-1.5 py-0.5 sm:py-1 rounded-full bg-black/40 backdrop-blur-md text-white/95 text-[11px] sm:text-xs font-semibold border border-white/15 shadow-sm">
                <button
                  onClick={handlePrevBanner}
                  aria-label="이전 배너"
                  className="p-1 hover:text-white text-white/80 active:scale-90 transition-all cursor-pointer outline-none focus:outline-none focus-visible:outline-none rounded-full"
                >
                  <ChevronLeft className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                </button>
                <span className="px-1 select-none tabular-nums">
                  {activeBannerIndex + 1} / {SPOTLIGHT_BANNERS.length}
                </span>
                <button
                  onClick={handleNextBanner}
                  aria-label="다음 배너"
                  className="p-1 hover:text-white text-white/80 active:scale-90 transition-all cursor-pointer outline-none focus:outline-none focus-visible:outline-none rounded-full"
                >
                  <ChevronRight className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
