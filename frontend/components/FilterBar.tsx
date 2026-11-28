"use client";

import { useState, useEffect, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { ChevronDown, Check, X, SlidersHorizontal } from "lucide-react";

interface FilterBarProps {
  selectedAge: string;
  onAgeChange: (age: string) => void;
  onFilterClick: () => void;
  showFilterButton?: boolean;
  isTextbook?: boolean;
  selectedTag?: string;
  onTagChange?: (tag: string) => void;
  disabledAges?: string[];
  rightSlot?: ReactNode;
  embedded?: boolean;
}

const AGE_OPTIONS = [
  { value: "", label: "전체 연령" },
  { value: "0-3", label: "0~3세" },
  { value: "4-7", label: "4~7세" },
  { value: "8-12", label: "8~12세" },
];

const AGE_CHIP_LABELS: Record<string, string> = {
  "0-3": "0~3세",
  "4-7": "4~7세",
  "8-12": "8~12세",
  "13+": "13세 이상",
  "teen": "13세 이상",
};

const TEXTBOOK_GRADE_OPTIONS = [
  { value: "", label: "전체 학년" },
  { value: "초등1학년", label: "초등 1학년" },
  { value: "초등2학년", label: "초등 2학년" },
  { value: "초등3학년", label: "초등 3학년" },
  { value: "초등4학년", label: "초등 4학년" },
  { value: "초등5학년", label: "초등 5학년" },
  { value: "초등6학년", label: "초등 6학년" },
];

export default function FilterBar({
  selectedAge,
  onAgeChange,
  onFilterClick,
  showFilterButton = true,
  isTextbook = false,
  selectedTag = "",
  onTagChange,
  disabledAges = [],
  rightSlot,
  embedded = false,
}: FilterBarProps) {
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isSheetOpen) {
      setIsAnimating(true);
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = "";
      };
    } else {
      const timer = setTimeout(() => setIsAnimating(false), 300);
      document.body.style.overflow = "";
      return () => clearTimeout(timer);
    }
  }, [isSheetOpen]);

  const isSelected = isTextbook
    ? Boolean(selectedTag && selectedTag !== "all")
    : Boolean(selectedAge);

  const chipLabel = isTextbook
    ? isSelected
      ? (TEXTBOOK_GRADE_OPTIONS.find((o) => o.value === selectedTag)?.label ?? selectedTag)
      : "학년"
    : isSelected
      ? (AGE_CHIP_LABELS[selectedAge] ?? selectedAge)
      : "연령";

  const handleSelectOption = (value: string) => {
    if (isTextbook) {
      onTagChange?.(value);
    } else {
      onAgeChange(value);
    }
    setIsSheetOpen(false);
  };

  const chips = (
    <>
      {/* 통합 필터 (정렬 등) 버튼 - 검색/작가 목록에서만 노출 */}
      {showFilterButton && (
        <button
          type="button"
          onClick={onFilterClick}
          className="shrink-0 inline-flex items-center gap-1 h-9 px-3 rounded-full text-[13.5px] font-medium transition-all cursor-pointer outline-none focus:outline-none active:scale-95 bg-white text-gray-700 border border-gray-200/90 active:bg-gray-50"
          aria-label="상세 필터 및 정렬"
        >
          <SlidersHorizontal className="w-3.5 h-3.5 text-gray-500" />
          <span>필터</span>
        </button>
      )}

      {/* 연령 / 학년 드롭다운 칩 (탭 시 바텀시트 오픈) */}
      <button
        type="button"
        onClick={() => setIsSheetOpen(true)}
        aria-label={isTextbook ? `학년 필터: ${chipLabel}` : `연령 필터: ${chipLabel}`}
        className={`shrink-0 inline-flex items-center gap-1 h-9 px-3.5 rounded-full text-[13.5px] transition-all cursor-pointer outline-none focus:outline-none active:scale-95 ${
          isSelected
            ? "bg-brand-primary text-white font-bold shadow-xs active:bg-brand-primary-dark"
            : "bg-white text-gray-700 font-semibold border border-gray-200/90 active:bg-gray-50"
        }`}
      >
        <span className="whitespace-nowrap">{chipLabel}</span>
        <ChevronDown
          className={`w-3.5 h-3.5 shrink-0 ${isSelected ? "text-white/90" : "text-gray-400"}`}
        />
      </button>
    </>
  );

  const sheetPortal =
    (isSheetOpen || isAnimating) &&
    typeof document !== "undefined" &&
    createPortal(
      <div className="fixed inset-0 z-[100] flex justify-center items-end sm:items-center pointer-events-none">
        {/* Overlay */}
        <div
          className={`absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity duration-300 pointer-events-auto ${
            isSheetOpen ? "opacity-100" : "opacity-0"
          }`}
          onClick={() => setIsSheetOpen(false)}
        />

        {/* Bottom Sheet */}
        <div
          className={`w-full max-w-md bg-white rounded-t-[28px] sm:rounded-[28px] shadow-2xl overflow-hidden pointer-events-auto transition-transform duration-300 transform ${
            isSheetOpen
              ? "translate-y-0 scale-100"
              : "translate-y-full sm:translate-y-8 sm:scale-95"
          } safe-area-bottom`}
        >
          <div className="p-6 pb-7 relative">
            {/* 우상단 X 닫기 버튼 */}
            <button
              type="button"
              onClick={() => setIsSheetOpen(false)}
              aria-label="닫기"
              className="absolute top-5 right-5 p-2 text-gray-400 active:scale-95 rounded-full active:bg-gray-100 transition-all outline-none focus:outline-none cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-lg font-bold text-gray-900 mb-4 pr-8">
              {isTextbook ? "학년 선택" : "연령 선택"}
            </h3>

            <div className="space-y-1.5 max-h-[60vh] overflow-y-auto">
              {(isTextbook ? TEXTBOOK_GRADE_OPTIONS : AGE_OPTIONS).map((option) => {
                const isOptionSelected = isTextbook
                  ? option.value === ""
                    ? !selectedTag || selectedTag === "all"
                    : selectedTag === option.value
                  : option.value === ""
                    ? !selectedAge
                    : selectedAge === option.value;

                const isDisabled =
                  !isTextbook &&
                  option.value !== "" &&
                  disabledAges.includes(option.value) &&
                  !isOptionSelected;

                return (
                  <button
                    key={option.value || "all"}
                    type="button"
                    disabled={isDisabled}
                    aria-disabled={isDisabled}
                    onClick={() => {
                      if (isDisabled) return;
                      handleSelectOption(option.value);
                    }}
                    className={`w-full min-h-[48px] px-4 py-3 rounded-2xl flex items-center justify-between text-left transition-all outline-none focus:outline-none ${
                      isDisabled
                        ? "bg-gray-50 text-gray-300 cursor-not-allowed"
                        : isOptionSelected
                          ? "bg-amber-50/80 text-brand-primary font-bold cursor-pointer"
                          : "bg-white text-gray-800 font-medium hover:bg-gray-50 active:bg-gray-100 cursor-pointer"
                    }`}
                  >
                    <span className="text-[15px]">{option.label}</span>
                    {isDisabled ? (
                      <span className="text-xs font-normal text-gray-300">도서 없음</span>
                    ) : isOptionSelected ? (
                      <Check className="w-5 h-5 text-brand-primary shrink-0" />
                    ) : null}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>,
      document.body
    );

  if (embedded) {
    return (
      <>
        <div className="inline-flex items-center gap-2 shrink-0">
          {chips}
        </div>
        {sheetPortal}
      </>
    );
  }

  return (
    <>
      <div className="w-full px-4 pt-1.5 pb-1.5 mb-2">
        <div className="w-full max-w-[1200px] mx-auto flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            {chips}
          </div>
          {rightSlot && (
            <div className="shrink-0 flex items-center">
              {rightSlot}
            </div>
          )}
        </div>
      </div>
      {sheetPortal}
    </>
  );
}
