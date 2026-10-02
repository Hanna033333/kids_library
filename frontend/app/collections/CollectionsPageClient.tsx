'use client'

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { BookOpen } from 'lucide-react';
import PageHeader from '@/components/PageHeader';
import Footer from '@/components/Footer';
import {
  UNIFIED_TAXONOMY,
  UnifiedCurationItem,
  SITUATION_PRESCRIPTIONS,
  SituationPrescription,
} from '@/lib/constants/curation-categories';
import { CURATION_THEME_SAMPLES } from '@/lib/constants/curation-samples';
import { CURATION_DOMINANT_COLORS } from '@/lib/constants/curation-colors';
import { sendGAEvent } from '@/lib/analytics';

function cleanTitle(title: string): string {
  if (!title) return '';
  return title
    .replace(
      /([\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD10-\uDDFF])/g,
      ''
    )
    .trim();
}

export default function CollectionsPageClient() {
  const [selectedSituation, setSelectedSituation] = useState<string>('all');

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

  return (
    <div className="min-h-screen bg-[#F5F5F8] flex flex-col justify-between">
      <div>
        {/* 상단 네비게이션 헤더 */}
        <PageHeader title="큐레이션 테마" showHome={true} />

        {/* 12대 발달/고민 맞춤 횡스크롤 스티키 탭 바 (Sticky Chip Bar) */}
        <div className="sticky top-[60px] z-40 bg-[#F5F5F8]/95 backdrop-blur-sm py-2.5 my-1.5">
          <div className="max-w-4xl mx-auto px-4 sm:px-6">
            <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-hide py-0.5">
              {SITUATION_PRESCRIPTIONS.map((prescription) => {
                const isSelected = selectedSituation === prescription.id;
                return (
                  <button
                    key={prescription.id}
                    onClick={() => handleSituationSelect(prescription)}
                    className={`shrink-0 px-4 py-2 rounded-full text-[14px] transition-all cursor-pointer outline-none focus:outline-none active:scale-95 ${
                      isSelected
                        ? 'bg-brand-primary text-white font-bold shadow-xs active:bg-brand-primary-dark'
                        : 'bg-white text-gray-700 font-medium border border-gray-200/80 active:bg-gray-100'
                    }`}
                  >
                    <span>{cleanTitle(prescription.name)}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* 4. 선택된 상황 처방 가이드 요약 배너 */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 pt-4 pb-2">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight leading-tight mb-1.5">
                {currentPrescription.title}
              </h2>
              <p className="text-xs sm:text-sm text-gray-500 leading-relaxed break-keep">
                {currentPrescription.description}
              </p>
            </div>
          </div>
        </div>

        {/* 4. 정갈한 2~3열 매거진 카드 그리드 (Uniform Magazine Card Grid) */}
        <main className="max-w-4xl mx-auto px-4 sm:px-6 py-4 pb-12">
          {filteredCurations.length === 0 ? (
            <div className="py-16 text-center bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-6">
              <p className="text-gray-600 font-bold text-base mb-1">
                해당 주제에 매칭된 큐레이션이 없습니다.
              </p>
              <button
                onClick={() => setSelectedSituation('all')}
                className="mt-4 px-4 py-2 bg-gray-100 active:bg-gray-200 text-gray-700 font-bold rounded-xl text-xs sm:text-sm transition-colors"
              >
                전체 큐레이션 보기
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-3 sm:gap-5">
              {filteredCurations.map((item) => {
                const sample =
                  CURATION_THEME_SAMPLES[item.tag] ||
                  CURATION_THEME_SAMPLES[item.slug];
                const covers = sample?.sample_covers || [];
                const mainCover = covers[0] || covers[1];
                const dominantColor =
                  CURATION_DOMINANT_COLORS[item.tag] ||
                  CURATION_DOMINANT_COLORS[item.slug] ||
                  '#1E293B';
                const displayTitle = cleanTitle(item.marketingTitle || item.title);

                return (
                  <Link
                    key={item.id}
                    href={`/collections/curation/${encodeURIComponent(item.slug)}`}
                    onClick={() => handleCardClick(item)}
                    className="group flex flex-col transition-all duration-300 active:scale-[0.98]"
                  >
                    {/* 🎨 매거진 포스터 카드 (책 표지 확대 + 표지 도미넌트 그라데이션 + 15자 마케팅 훅 타이포) */}
                    <div
                      className="relative w-full aspect-[3.2/4] sm:aspect-[3.6/4.6] rounded-xl sm:rounded-2xl overflow-hidden shadow-xs hover:shadow-lg transition-all duration-300"
                      style={{ backgroundColor: dominantColor }}
                    >
                      {/* 1. 배경 확대 책 표지 (Cover art bleed at bottom) */}
                      {mainCover ? (
                        <div className="absolute inset-0 w-full h-full overflow-hidden select-none">
                          <Image
                            src={mainCover}
                            alt=""
                            fill
                            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
                            className="object-cover object-bottom w-full h-full transform group-hover:scale-105 transition-transform duration-700 ease-out"
                            unoptimized
                          />
                        </div>
                      ) : (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <BookOpen className="w-10 h-10 text-white/40" />
                        </div>
                      )}

                      {/* 2. 상단 책 표지 도미넌트 그라데이션 오버레이 (텍스트 가독성 확보) */}
                      <div
                        className="absolute inset-x-0 top-0 h-[58%] sm:h-[60%] pointer-events-none z-1"
                        style={{
                          background: `linear-gradient(to bottom, ${dominantColor} 0%, ${dominantColor} 48%, transparent 100%)`,
                        }}
                      />

                      {/* 3. 포스터 내부 컨텐츠 */}
                      <div className="relative z-10 h-full p-3 sm:p-4 flex flex-col justify-between select-none">
                        {/* 상단 헤더 & 마케팅 훅 타이틀 */}
                        <div>
                          {/* 상단 태그 */}
                          <div className="flex items-center mb-2 sm:mb-2.5">
                            <span className="text-[10px] sm:text-[11.5px] font-bold text-white/95 bg-black/40 backdrop-blur-md px-2.5 py-0.5 rounded-full border border-white/15">
                              #{cleanTitle(item.tag)}
                            </span>
                          </div>

                          {/* 15자 이내 마케팅 훅 타이틀 (말줄임표 없이 완결된 문구로 시원하게 노출) */}
                          <h3 className="text-[17.5px] sm:text-[21px] md:text-[23px] font-bold leading-[1.28] text-white tracking-tight break-keep">
                            {displayTitle}
                          </h3>
                        </div>
                      </div>
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
