"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { sendGAEvent } from "@/lib/analytics";
import { ALL_TAXONOMY } from "@/lib/constants/taxonomy";
import { TAG_SYNONYMS } from "@/lib/constants/curation-categories";

interface SearchDiscoveryHubProps {
  onSearchKeyword?: (keyword: string) => void;
  onSelectAge?: (age: string) => void;
  onSelectCuration?: (curation: string, tag?: string) => void;
}

interface TrendingItem {
  rank: number;
  keyword: string;
  bookId?: number | string;
  author?: string;
  query?: string;
  tag?: string;
  curation?: string;
  age?: string;
  change: "up" | "down" | "same" | "new";
  diff?: number;
}

const AGE_TABS = [
  { key: "all", label: "전체" },
  { key: "0-3", label: "0~3세" },
  { key: "4-7", label: "4~7세" },
  { key: "8-12", label: "8~12세" },
  { key: "13+", label: "13세+" },
];

// 목적지 URL 생성기 (책 제목: 도서 상세 / 작가: 작가 전용 리스트 / 테마: 큐레이션 리스트)
export function getDestinationUrl(item: { bookId?: number | string; author?: string; tag?: string; curation?: string; age?: string; query?: string }): string {
  // 1. 📖 책 제목 (도서 상세 페이지로 직결)
  if (item.bookId) {
    return `/book/${item.bookId}`;
  }

  // 2. ✍️ 작가명 (작가 전용 큐레이션 리스트 페이지)
  if (item.author) {
    return `/books?author=${encodeURIComponent(item.author)}`;
  }

  const rawKey = item.curation || item.tag || "";
  const curationKey = TAG_SYNONYMS[rawKey] || rawKey;

  // 3. 🏷️ 특수 큐레이션
  if (["caldecott", "칼데콧", "칼데콧 수상작"].includes(curationKey)) {
    const ageParam = item.age ? `?age=${encodeURIComponent(item.age)}` : "";
    return `/collections/curation/caldecott${ageParam}`;
  }
  if (["textbook", "교과서수록", "초등 국어 교과서", "초등 교과서 수록도서"].includes(curationKey)) {
    return `/collections/curation/textbook`;
  }
  if (["research-council", "어린이도서연구회", "어린이도서연구회 추천"].includes(curationKey)) {
    const ageParam = item.age ? `?age=${encodeURIComponent(item.age)}` : "";
    return `/collections/curation/research-council${ageParam}`;
  }
  if (["winter-vacation", "겨울방학", "겨울방학2026"].includes(curationKey)) {
    return `/collections/curation/winter-vacation`;
  }
  if (["summer-vacation", "여름방학", "여름방학2026"].includes(curationKey)) {
    return `/collections/curation/summer-vacation`;
  }

  // 4. 🏷️ ALL_TAXONOMY 테마 큐레이션 매칭
  const targetTag = item.tag ? (TAG_SYNONYMS[item.tag] || item.tag) : undefined;
  if (targetTag) {
    const matched = ALL_TAXONOMY.find((t) => t.tag === targetTag || t.slug === targetTag);
    if (matched) {
      const ageParam = item.age ? `?age=${encodeURIComponent(item.age)}` : "";
      return `/collections/curation/${encodeURIComponent(matched.slug)}${ageParam}`;
    }
  }

  // 5. curation 키 직접 매칭
  if (item.curation) {
    const targetCuration = TAG_SYNONYMS[item.curation] || item.curation;
    const matched = ALL_TAXONOMY.find((t) => t.tag === targetCuration || t.slug === targetCuration);
    if (matched) {
      const ageParam = item.age ? `?age=${encodeURIComponent(item.age)}` : "";
      return `/collections/curation/${encodeURIComponent(matched.slug)}${ageParam}`;
    }
    const ageParam = item.age ? `&age=${encodeURIComponent(item.age)}` : "";
    return `/books?curation=${encodeURIComponent(item.curation)}${ageParam}`;
  }

  // 6. 검색 쿼리
  if (item.query) {
    return `/books?q=${encodeURIComponent(item.query)}`;
  }

  // 7. 일반 태그 매칭 폴백
  if (item.tag) {
    const ageParam = item.age ? `&age=${encodeURIComponent(item.age)}` : "";
    return `/books?curation=${encodeURIComponent(item.tag)}${ageParam}`;
  }

  return "/collections";
}

const TRENDING_BY_AGE: Record<string, TrendingItem[]> = {
  all: [
    { rank: 1, keyword: "잠자리 그림책", tag: "잠자리", change: "same" },
    { rank: 2, keyword: "알사탕", bookId: 9804, change: "up", diff: 1 },
    { rank: 3, keyword: "백희나", author: "백희나", change: "down", diff: 1 },
    { rank: 4, keyword: "초등 교과서 수록도서", curation: "교과서수록", change: "up", diff: 3 },
    { rank: 5, keyword: "수박 수영장", bookId: 9505, change: "same" },
    { rank: 6, keyword: "칼데콧 수상작", curation: "caldecott", change: "new" },
    { rank: 7, keyword: "달님 안녕", bookId: 8437, change: "down", diff: 2 },
    { rank: 8, keyword: "단단한 자존감", tag: "자존감", change: "up", diff: 1 },
    { rank: 9, keyword: "앤서니 브라운", author: "앤서니 브라운", change: "down", diff: 1 },
    { rank: 10, keyword: "구름빵", bookId: 7817, change: "same" },
  ],
  "0-3": [
    { rank: 1, keyword: "사과가 쿵!", bookId: 9245, change: "same" },
    { rank: 2, keyword: "달님 안녕", bookId: 8437, change: "up", diff: 2 },
    { rank: 3, keyword: "스르륵 잠자리", tag: "잠자리", age: "0-3", change: "new" },
    { rank: 4, keyword: "감기 걸린 물고기", bookId: 7614, change: "down", diff: 1 },
    { rank: 5, keyword: "깨끗한 생활습관", tag: "생활습관", age: "0-3", change: "same" },
    { rank: 6, keyword: "사랑스러운 동물", tag: "생명존중", age: "0-3", change: "up", diff: 1 },
    { rank: 7, keyword: "오감 자극 놀이", tag: "신체활동", age: "0-3", change: "down", diff: 2 },
    { rank: 8, keyword: "엄마 아빠 가족사랑", tag: "가족사랑", age: "0-3", change: "same" },
    { rank: 9, keyword: "씽씽 달리는 탈것", tag: "탈것", age: "0-3", change: "up", diff: 1 },
    { rank: 10, keyword: "웃음 빵빵 유머", tag: "유머", age: "0-3", change: "down", diff: 1 },
  ],
  "4-7": [
    { rank: 1, keyword: "알사탕", bookId: 9804, change: "same" },
    { rank: 2, keyword: "백희나", author: "백희나", change: "up", diff: 1 },
    { rank: 3, keyword: "장수탕 선녀님", bookId: 10477, change: "down", diff: 1 },
    { rank: 4, keyword: "유치원·학교 적응", tag: "적응", age: "4-7", change: "up", diff: 2 },
    { rank: 5, keyword: "수박 수영장", bookId: 9505, change: "same" },
    { rank: 6, keyword: "칼데콧 수상작", curation: "caldecott", age: "4-7", change: "new" },
    { rank: 7, keyword: "단단한 자존감", tag: "자존감", age: "4-7", change: "down", diff: 2 },
    { rank: 8, keyword: "앤서니 브라운", author: "앤서니 브라운", change: "up", diff: 1 },
    { rank: 9, keyword: "마음 다스리기", tag: "감정조절", age: "4-7", change: "down", diff: 1 },
    { rank: 10, keyword: "거대한 공룡 탐험", tag: "공룡", age: "4-7", change: "same" },
  ],
  "8-12": [
    { rank: 1, keyword: "초등 국어 교과서", curation: "교과서수록", age: "8-12", change: "same" },
    { rank: 2, keyword: "푸른 사자 와니니", bookId: 11008, change: "up", diff: 2 },
    { rank: 3, keyword: "어린이도서연구회 추천", curation: "어린이도서연구회", age: "8-12", change: "down", diff: 1 },
    { rank: 4, keyword: "지각대장 존", bookId: 10598, change: "up", diff: 1 },
    { rank: 5, keyword: "고양이 해결사 깜냥", bookId: 7734, change: "new" },
    { rank: 6, keyword: "이수지", author: "이수지", change: "down", diff: 2 },
    { rank: 7, keyword: "구수한 옛이야기", tag: "전래동화", age: "8-12", change: "same" },
    { rank: 8, keyword: "지혜로운 역사 이야기", tag: "역사이야기", age: "8-12", change: "up", diff: 1 },
    { rank: 9, keyword: "호기심 과학 원리", tag: "과학원리", age: "8-12", change: "down", diff: 1 },
    { rank: 10, keyword: "스스로 자존감", tag: "자존감", age: "8-12", change: "same" },
  ],
  "13+": [
    { rank: 1, keyword: "아몬드", bookId: 11517, change: "same" },
    { rank: 2, keyword: "어린 왕자", bookId: 9882, change: "up", diff: 1 },
    { rank: 3, keyword: "내 꿈을 찾는 진로", tag: "진로", age: "13+", change: "down", diff: 1 },
    { rank: 4, keyword: "청소년 문학상", query: "청소년 문학", change: "up", diff: 3 },
    { rank: 5, keyword: "세계 역사와 문화", tag: "세계역사", age: "13+", change: "same" },
    { rank: 6, keyword: "호기심 가득 판타지", tag: "판타지", age: "13+", change: "new" },
    { rank: 7, keyword: "다정한 내 친구", tag: "우정", age: "13+", change: "down", diff: 2 },
    { rank: 8, keyword: "평화를 지키는 마음", tag: "평화", age: "13+", change: "same" },
    { rank: 9, keyword: "따뜻한 위로와 힐링", tag: "위로", age: "13+", change: "up", diff: 1 },
    { rank: 10, keyword: "포기하지 않는 끈기", tag: "끈기", age: "13+", change: "down", diff: 1 },
  ],
};

const RECOMMENDED_TAGS = [
  { label: "잠자리 독서", tag: "잠자리" },
  { label: "유치원 적응", tag: "적응" },
  { label: "자존감 형성", tag: "자존감" },
  { label: "감정 표현", tag: "감정조절" },
  { label: "첫 사회성", tag: "사회성" },
  { label: "공룡과 모험", tag: "공룡" },
  { label: "자연관찰", tag: "자연관찰" },
  { label: "과학 호기심", tag: "과학원리" },
  { label: "가족 사랑", tag: "가족사랑" },
  { label: "예술 감성", tag: "예술감성" },
  { label: "교과서 수록", curation: "교과서수록" },
  { label: "칼데콧 수상작", curation: "caldecott" },
];

export default function SearchDiscoveryHub({
  onSearchKeyword,
  onSelectAge,
  onSelectCuration,
}: SearchDiscoveryHubProps) {
  const router = useRouter();
  const [selectedAgeTab, setSelectedAgeTab] = useState("all");

  // 사용자 이전 선택 연령이 있으면 기본 탭으로 자동 적용
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedAge = localStorage.getItem("lastSelectedAge");
      if (savedAge && ["0-3", "4-7", "8-12", "13+", "teen"].includes(savedAge)) {
        const normalized = savedAge === "teen" ? "13+" : savedAge;
        setSelectedAgeTab(normalized);
      }
    }
  }, []);

  // 동적 기준 시간 (예: "09.18 11:00 기준")
  const timestampText = useMemo(() => {
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hours = String(now.getHours()).padStart(2, "0");
    return `${month}.${day} ${hours}:00 기준`;
  }, []);

  const handleTabChange = (key: string) => {
    setSelectedAgeTab(key);
    sendGAEvent("search_hub_age_tab", { age_tab: key });
  };

  const handleKeywordClick = (item: TrendingItem) => {
    const targetUrl = getDestinationUrl(item);
    const itemType = item.bookId ? "book" : item.author ? "author_collection" : item.query ? "search" : "curation";

    sendGAEvent("search_hub_click", {
      type: "trending_keyword",
      keyword: item.keyword,
      item_type: itemType,
      target_url: targetUrl,
      age_tab: selectedAgeTab,
    });

    router.push(targetUrl);
  };

  const handleTagClick = (item: typeof RECOMMENDED_TAGS[0]) => {
    const targetUrl = getDestinationUrl(item);
    sendGAEvent("search_hub_click", {
      type: "recommended_tag",
      label: item.label,
      target_url: targetUrl,
    });
    router.push(targetUrl);
  };

  const currentTrendingList = TRENDING_BY_AGE[selectedAgeTab] || TRENDING_BY_AGE.all;

  // 등락 뱃지 렌더러
  const renderTrendChange = (item: TrendingItem) => {
    if (item.change === "new") {
      return (
        <span className="text-[10px] font-black text-amber-500 tracking-tight shrink-0">
          NEW
        </span>
      );
    }
    if (item.change === "up") {
      return (
        <span className="inline-flex items-center text-[11px] font-extrabold text-rose-500 shrink-0">
          <span className="text-[9px] mr-0.5">▲</span>
          {item.diff}
        </span>
      );
    }
    if (item.change === "down") {
      return (
        <span className="inline-flex items-center text-[11px] font-extrabold text-blue-500 shrink-0">
          <span className="text-[9px] mr-0.5">▼</span>
          {item.diff}
        </span>
      );
    }
    return (
      <span className="text-[12px] font-bold text-gray-300 shrink-0 select-none">
        -
      </span>
    );
  };

  return (
    <div className="w-full max-w-[1200px] mx-auto px-4 sm:px-6 py-2 space-y-6">
      {/* 🌟 1. 실시간 또래 인기 검색어 Top 10 */}
      <section className="bg-white rounded-2xl p-5 sm:p-6 shadow-[0_1px_4px_rgba(0,0,0,0.06)] border border-gray-100/80">
        {/* 2단 타이틀 */}
        <div className="mb-3.5">
          <span className="text-[13px] text-gray-500 font-semibold block mb-0.5">
            실시간 검색 트렌드
          </span>
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 leading-tight">
            {selectedAgeTab === "all" ? "지금 많이 찾는 인기 검색어" : `${AGE_TABS.find(t => t.key === selectedAgeTab)?.label} 또래 부모가 많이 찾은 검색어`}
          </h2>
        </div>

        {/* 연령 선택 필터 탭 */}
        <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-hide pb-3.5 mb-2 border-b border-gray-100/80">
          {AGE_TABS.map((tab) => {
            const isSelected = selectedAgeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => handleTabChange(tab.key)}
                className={`px-3.5 py-1.5 rounded-full text-xs sm:text-[13px] font-bold transition-all shrink-0 cursor-pointer ${
                  isSelected
                    ? "bg-gray-900 text-white shadow-xs"
                    : "bg-gray-100 text-gray-600 active:bg-gray-200"
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* 2열 균등 그리드 (1~5위 좌측, 6~10위 우측) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8">
          {/* 1~5위 */}
          <div className="divide-y divide-gray-100/80">
            {currentTrendingList.slice(0, 5).map((item) => (
              <button
                key={item.rank}
                onClick={() => handleKeywordClick(item)}
                className="w-full flex items-center justify-between py-3 px-2 active:bg-gray-100 rounded-lg transition-colors group cursor-pointer text-left"
              >
                <div className="flex items-center gap-3.5 min-w-0 pr-2">
                  <span
                    className={`w-5 text-center text-sm sm:text-base ${
                      item.rank <= 3
                        ? "font-extrabold text-gray-900"
                        : "font-semibold text-gray-400"
                    }`}
                  >
                    {item.rank}
                  </span>
                  <span className="text-sm sm:text-[15px] font-medium text-gray-800 truncate transition-colors">
                    {item.keyword}
                  </span>
                </div>
                {renderTrendChange(item)}
              </button>
            ))}
          </div>

          {/* 6~10위 */}
          <div className="divide-y divide-gray-100/80">
            {currentTrendingList.slice(5, 10).map((item) => (
              <button
                key={item.rank}
                onClick={() => handleKeywordClick(item)}
                className="w-full flex items-center justify-between py-3 px-2 active:bg-gray-100 rounded-lg transition-colors group cursor-pointer text-left"
              >
                <div className="flex items-center gap-3.5 min-w-0 pr-2">
                  <span className="w-5 text-center font-semibold text-xs sm:text-sm text-gray-400">
                    {item.rank}
                  </span>
                  <span className="text-sm sm:text-[15px] font-medium text-gray-800 truncate transition-colors">
                    {item.keyword}
                  </span>
                </div>
                {renderTrendChange(item)}
              </button>
            ))}
          </div>
        </div>

        {/* 🕒 하단 기준 타임스탬프 */}
        <div className="mt-3 pt-2 text-right">
          <span className="text-[11px] text-gray-400 font-medium">
            {timestampText}
          </span>
        </div>
      </section>

      {/* 🌟 2. 아이 상황·발달별 맞춤 테마 칩 */}
      <section className="bg-white rounded-2xl p-5 sm:p-6 shadow-[0_1px_4px_rgba(0,0,0,0.06)] border border-gray-100/80">
        <div className="mb-4">
          <span className="text-[13px] text-gray-500 font-semibold block mb-0.5">
            아이 마음 & 양육 상황
          </span>
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 leading-tight">
            상황별 추천 키워드
          </h2>
        </div>

        <div className="flex flex-wrap gap-2 sm:gap-2.5">
          {RECOMMENDED_TAGS.map((item) => (
            <button
              key={item.label}
              onClick={() => handleTagClick(item)}
              className="px-3.5 py-2 rounded-full text-xs sm:text-[13px] font-medium transition-all active:scale-95 cursor-pointer bg-gray-50 active:bg-gray-100 text-gray-700 border border-gray-200/80 shadow-2xs"
            >
              {item.label}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
