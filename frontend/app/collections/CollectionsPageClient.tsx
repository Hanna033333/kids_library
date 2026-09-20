'use client'

import React, { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Sparkles, BookOpen, ChevronLeft, ChevronRight, ArrowRight } from 'lucide-react';
import PageHeader from '@/components/PageHeader';
import Footer from '@/components/Footer';
import {
  UNIFIED_TAXONOMY,
  UnifiedCurationItem,
  SITUATION_PRESCRIPTIONS,
  SituationPrescription,
} from '@/lib/constants/curation-categories';
import { CURATION_THEME_SAMPLES } from '@/lib/constants/curation-samples';
import { sendGAEvent } from '@/lib/analytics';

// 🌟 에디터 스포트라이트 배너 3종 정의
const SPOTLIGHT_BANNERS = [
  {
    id: 'sleep',
    badge: '🌙 수면 의식 큐레이션',
    title: '스르륵 꿀잠 그림책',
    description: '밤마다 잠투정하는 아이를 위해. 잠들기 전 포근하고 차분한 수면 의식을 선물하는 베스트 그림책 컬렉션',
    slug: 'sleep',
    tag: '잠자리',
    count: 32,
    bgGradient: 'from-slate-900 via-indigo-950 to-slate-900',
    accentColor: 'text-amber-300',
    badgeBg: 'bg-amber-400/20 text-amber-300 border-amber-400/30',
    glowColor: 'bg-amber-500/20',
  },
  {
    id: 'self-esteem',
    badge: '✨ 자존감 & 마음 성장',
    title: '단단한 자존감 그림책',
    description: '기죽지 않고 씩씩하게! 실수해도 괜찮다고 다정하게 용기를 북돋워 주는 마음 성장 그림책 모음',
    slug: 'self-esteem',
    tag: '자존감',
    count: 34,
    bgGradient: 'from-amber-950 via-stone-900 to-amber-900',
    accentColor: 'text-amber-200',
    badgeBg: 'bg-rose-400/20 text-rose-200 border-rose-400/30',
    glowColor: 'bg-rose-500/20',
  },
  {
    id: 'textbook',
    badge: '📖 초등 국어 수업 연계',
    title: '초등 교과서 수록도서',
    description: '초등 1~6학년 국어 교과서에 실제로 실린 검증된 필독서! 생각하는 힘과 문해력을 키워줘요',
    slug: 'textbook',
    tag: '교과서수록',
    count: 197,
    bgGradient: 'from-emerald-950 via-teal-950 to-slate-900',
    accentColor: 'text-emerald-300',
    badgeBg: 'bg-emerald-400/20 text-emerald-300 border-emerald-400/30',
    glowColor: 'bg-emerald-500/20',
  },
];

export default function CollectionsPageClient() {
  const [selectedSituation, setSelectedSituation] = useState<string>('all');
  const [activeBannerIndex, setActiveBannerIndex] = useState<number>(0);
  const [isPaused, setIsPaused] = useState<boolean>(false);

  // 5초 자동 롤링 타이머
  useEffect(() => {
    if (isPaused) return;
    const timer = setInterval(() => {
      setActiveBannerIndex((prev) => (prev + 1) % SPOTLIGHT_BANNERS.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [isPaused]);

  const handlePrevBanner = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setActiveBannerIndex((prev) =>
      prev === 0 ? SPOTLIGHT_BANNERS.length - 1 : prev - 1
    );
  };

  const handleNextBanner = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setActiveBannerIndex((prev) => (prev + 1) % SPOTLIGHT_BANNERS.length);
  };

  const currentPrescription = useMemo(() => {
    return (
      SITUATION_PRESCRIPTIONS.find((p) => p.id === selectedSituation) ||
      SITUATION_PRESCRIPTIONS[0]
    );
  }, [selectedSituation]);

  const filteredCurations = useMemo(() => {
    if (selectedSituation === 'all') {
      return UNIFIED_TAXONOMY;
    }
    const current = SITUATION_PRESCRIPTIONS.find((p) => p.id === selectedSituation);
    if (!current || current.tags.length === 0) return UNIFIED_TAXONOMY;

    return UNIFIED_TAXONOMY.filter((item) =>
      current.tags.some((t) => t === item.tag || t === item.slug)
    );
  }, [selectedSituation]);

  const handleSituationSelect = (prescription: SituationPrescription) => {
    setSelectedSituation(prescription.id);
    sendGAEvent('click_curation_situation_tab', { situation_id: prescription.id });
  };

  const handleCardClick = (item: UnifiedCurationItem) => {
    sendGAEvent('click_curation_hub_card', {
      curation_slug: item.slug,
      curation_tag: item.tag,
      curation_title: item.title,
      situation_id: selectedSituation,
    });
  };

  // 현재 활성화된 스포트라이트 배너
  const currentBanner = SPOTLIGHT_BANNERS[activeBannerIndex];
  const spotlightSample =
    CURATION_THEME_SAMPLES[currentBanner.tag] ||
    CURATION_THEME_SAMPLES[currentBanner.slug];
  const spotlightCovers = spotlightSample?.sample_covers || [];

  return (
    <div className="min-h-screen bg-[#F5F5F8] flex flex-col justify-between">
      <div>
        {/* 상단 네비게이션 헤더 */}
        <PageHeader title="큐레이션 테마" showHome={true} />

        {/* 🌟 1. 이번 주 에디터 스포트라이트 롤링 캐러셀 배너 (150% 최적 높이) */}
        <div
          className="px-4 sm:px-6 pt-3.5 pb-2 max-w-4xl mx-auto w-full relative"
          onMouseEnter={() => setIsPaused(true)}
          onMouseLeave={() => setIsPaused(false)}
        >
          <div className="relative overflow-hidden rounded-2xl sm:rounded-3xl shadow-md border border-slate-700/40">
            <Link
              href={`/collections/curation/${encodeURIComponent(currentBanner.slug)}`}
              onClick={() =>
                sendGAEvent('click_spotlight_banner', {
                  banner_slug: currentBanner.slug,
                  banner_title: currentBanner.title,
                  index: activeBannerIndex,
                })
              }
              className={`group relative block px-5 py-6 sm:px-7 sm:py-7 text-white transition-all duration-500 bg-gradient-to-br ${currentBanner.bgGradient}`}
            >
              {/* 배경 은은한 별빛/컬러 글로우 */}
              <div
                className={`absolute -top-12 -right-12 w-44 h-44 ${currentBanner.glowColor} rounded-full blur-3xl pointer-events-none transition-all duration-500`}
              />
              <div className="absolute -bottom-12 -left-12 w-44 h-44 bg-white/5 rounded-full blur-3xl pointer-events-none" />

              <div className="flex items-center justify-between gap-4 sm:gap-6">
                {/* 좌측: 타이틀 & 서브 설명 */}
                <div className="relative z-10 flex-1 min-w-0 pl-1">
                  <h1 className="text-xl sm:text-2xl font-black leading-tight tracking-tight mb-1.5 text-white line-clamp-1">
                    {currentBanner.title}
                  </h1>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed break-keep max-w-md line-clamp-2">
                    {currentBanner.description}
                  </p>
                </div>

                {/* 우측: 입체 도서 아트 쇼케이스 (150% 크기) */}
                <div className="relative z-10 shrink-0 flex items-center justify-end h-24 sm:h-28 w-34 sm:w-42 pr-1 select-none pointer-events-none">
                  {spotlightCovers.length > 0 ? (
                    <div className="relative w-full h-full flex items-center justify-end">
                      {/* 뒤쪽 도서 */}
                      {spotlightCovers[1] && (
                        <div className="absolute right-8 sm:right-10 bottom-0.5 w-[46px] sm:w-[54px] h-[66px] sm:h-[78px] rounded-sm shadow-md overflow-hidden transform -rotate-10 opacity-75 transition-all duration-300 border border-white/20 bg-slate-800">
                          <Image
                            src={spotlightCovers[1]}
                            alt=""
                            fill
                            sizes="60px"
                            className="object-cover"
                            unoptimized
                          />
                        </div>
                      )}

                      {/* 앞쪽 메인 도서 */}
                      <div className="relative z-20 right-0 bottom-0 w-[54px] sm:w-[64px] h-[78px] sm:h-[90px] rounded-md shadow-lg overflow-hidden transform rotate-6 transition-all duration-300 border border-white/30 bg-slate-800">
                        <Image
                          src={spotlightCovers[0] || spotlightCovers[1]}
                          alt=""
                          fill
                          sizes="80px"
                          className="object-cover"
                          unoptimized
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="w-13 h-18 rounded-md bg-slate-800 border border-slate-700 flex items-center justify-center text-amber-400">
                      <BookOpen className="w-6 h-6" />
                    </div>
                  )}
                </div>
              </div>
            </Link>

            {/* 좌우 네비게이션 화살표 버튼 */}
            <button
              onClick={handlePrevBanner}
              aria-label="이전 배너"
              className="absolute left-2 top-1/2 -translate-y-1/2 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-black/40 active:bg-black/70 text-white flex items-center justify-center backdrop-blur-xs transition-all active:scale-90 z-30"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={handleNextBanner}
              aria-label="다음 배너"
              className="absolute right-2 top-1/2 -translate-y-1/2 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-black/40 active:bg-black/70 text-white flex items-center justify-center backdrop-blur-xs transition-all active:scale-90 z-30"
            >
              <ChevronRight className="w-4 h-4" />
            </button>

            {/* 하단 페이지 인디케이터 도트 */}
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex items-center gap-1.5 z-30">
              {SPOTLIGHT_BANNERS.map((_, idx) => (
                <button
                  key={idx}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setActiveBannerIndex(idx);
                  }}
                  aria-label={`슬라이드 ${idx + 1}`}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    activeBannerIndex === idx
                      ? 'w-5 bg-white shadow-xs'
                      : 'w-1.5 bg-white/40'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* 🩺 2. 상황별 맞춤 처방전 탭 (Sticky Bar) */}
        <div className="sticky top-[60px] z-40 bg-[#F5F5F8]/95 backdrop-blur-sm border-b border-gray-200/60 py-3 px-4 sm:px-6">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-hide py-0.5">
              {SITUATION_PRESCRIPTIONS.map((prescription) => {
                const isSelected = selectedSituation === prescription.id;
                return (
                  <button
                    key={prescription.id}
                    onClick={() => handleSituationSelect(prescription)}
                    className={`inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full text-xs sm:text-sm font-bold whitespace-nowrap transition-all active:scale-95 shrink-0 ${
                      isSelected
                        ? 'bg-gray-900 text-white shadow-sm'
                        : 'bg-white text-gray-600 border border-gray-200 active:bg-gray-100'
                    }`}
                  >
                    <span>{prescription.icon}</span>
                    <span>{prescription.name}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* 3. 선택된 상황 처방 가이드 요약 배너 */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 pt-5 pb-1">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-base">{currentPrescription.icon}</span>
                <h2 className="text-base sm:text-lg font-black text-gray-900">
                  {currentPrescription.title}
                </h2>
              </div>
              <p className="text-xs sm:text-sm text-gray-500 leading-relaxed break-keep">
                {currentPrescription.description}
              </p>
            </div>
            <span className="shrink-0 text-xs font-bold text-gray-400 bg-gray-100 px-2.5 py-1 rounded-full">
              {filteredCurations.length}개 테마
            </span>
          </div>
        </div>

        {/* 4. 2단 리스트 와이드 카드 그리드 */}
        <main className="max-w-4xl mx-auto px-4 sm:px-6 py-4 pb-12">
          {filteredCurations.length === 0 ? (
            <div className="py-16 text-center bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-6">
              <p className="text-gray-600 font-bold text-base mb-1">
                해당 상황에 매칭된 테마가 없습니다.
              </p>
              <button
                onClick={() => setSelectedSituation('all')}
                className="mt-4 px-4 py-2 bg-gray-100 active:bg-gray-200 text-gray-700 font-bold rounded-xl text-xs sm:text-sm transition-colors"
              >
                전체 테마 보기
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              {filteredCurations.map((item) => {
                const sample =
                  CURATION_THEME_SAMPLES[item.tag] || CURATION_THEME_SAMPLES[item.slug];
                const covers = sample?.sample_covers || [];
                const sampleTitles = sample?.sample_titles || [];

                // 서브 설명 텍스트 (대표 도서 목록이 있으면 도서 목록, 없으면 서브타이틀)
                const descText =
                  sampleTitles.length > 0
                    ? `${sampleTitles.join(', ')} 등`
                    : item.subtitle;

                return (
                  <Link
                    key={item.id}
                    href={`/collections/curation/${encodeURIComponent(item.slug)}`}
                    onClick={() => handleCardClick(item)}
                    className="group relative overflow-hidden bg-white rounded-2xl p-4 sm:p-5 shadow-[0_1px_4px_rgba(0,0,0,0.06)] border border-gray-100/90 transition-all duration-200 flex items-center justify-between min-h-[116px] sm:min-h-[124px] active:scale-[0.99]"
                  >
                    {/* 우측 앰비언트 라이트 배경 효과 */}
                    <div className="absolute right-0 top-0 bottom-0 w-36 bg-gradient-to-l from-amber-50/40 via-gray-50/20 to-transparent pointer-events-none" />

                    {/* 좌측: 타이틀 & 서브 설명 */}
                    <div className="flex-1 pr-3 sm:pr-4 z-10 min-w-0 flex flex-col justify-center self-stretch">
                      {/* 메인 테마 타이틀 */}
                      <h2 className="text-[15px] sm:text-[17px] font-black text-gray-900 leading-snug line-clamp-1 mb-1.5">
                        {item.title}
                      </h2>

                      {/* 서브 설명 / 대표 도서 목록 (캡처 스타일) */}
                      <p className="text-xs sm:text-[13px] text-gray-500 font-normal leading-relaxed line-clamp-2 break-keep">
                        {descText}
                      </p>
                    </div>

                    {/* 우측: 대표 도서 입체 표지 아트 (캡처 스타일) */}
                    <div className="relative w-[76px] sm:w-[88px] h-[92px] sm:h-[104px] shrink-0 flex items-center justify-end z-10 select-none pointer-events-none">
                      {covers.length > 0 ? (
                        <div className="relative w-full h-full flex items-center justify-end">
                          {/* 2번째 도서 (뒤쪽 도서 - 살짝 왼쪽으로 겹침) */}
                          {covers.length > 1 && (
                            <div className="absolute right-7 sm:right-9 bottom-1 w-[46px] sm:w-[54px] h-[64px] sm:h-[76px] rounded-[4px] shadow-sm overflow-hidden transform -rotate-[8deg] opacity-75 transition-all duration-300 border border-black/5 bg-gray-100">
                              <Image
                                src={covers[1]}
                                alt=""
                                fill
                                sizes="60px"
                                className="object-cover"
                                unoptimized
                              />
                            </div>
                          )}

                          {/* 1번째 도서 (앞쪽 메인 도서 - 살짝 오른쪽으로 회전) */}
                          <div className="relative right-0 sm:right-1 bottom-0 w-[54px] sm:w-[62px] h-[76px] sm:h-[88px] rounded-[5px] shadow-md overflow-hidden transform rotate-[6deg] transition-all duration-300 border border-black/10 bg-gray-100">
                            <Image
                              src={covers[0]}
                              alt=""
                              fill
                              sizes="80px"
                              className="object-cover"
                              unoptimized
                            />
                          </div>
                        </div>
                      ) : (
                        <div className="w-[52px] h-[72px] rounded-md bg-amber-50 border border-amber-200/60 flex items-center justify-center text-amber-500 shadow-xs">
                          <BookOpen className="w-5 h-5 opacity-60" />
                        </div>
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </main>
      </div>

      <Footer />
    </div>
  );
}
