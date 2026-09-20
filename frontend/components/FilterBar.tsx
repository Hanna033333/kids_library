interface FilterBarProps {
  selectedAge: string;
  onAgeChange: (age: string) => void;
  onFilterClick: () => void;
  showFilterButton?: boolean;
  isTextbook?: boolean;
  selectedTag?: string;
  onTagChange?: (tag: string) => void;
}

const AGE_OPTIONS = [
  { value: "0-3", label: "0~3세" },
  { value: "4-7", label: "4~7세" },
  { value: "8-12", label: "8~12세" },
];

const TEXTBOOK_GRADE_OPTIONS = [
  { value: "all", label: "전체" },
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
  onTagChange
}: FilterBarProps) {

  const handleAgeToggle = (ageVal: string) => {
    if (selectedAge === ageVal) {
      onAgeChange(""); // Toggle off
    } else {
      onAgeChange(ageVal);
    }
  };

  const handleTagToggle = (tagVal: string) => {
    if (tagVal === "all" || tagVal === "") {
      onTagChange?.(""); // 전체 선택
    } else if (selectedTag === tagVal) {
      onTagChange?.(""); // Toggle off -> 전체로 복귀
    } else {
      onTagChange?.(tagVal);
    }
  };

  return (
    <div className="w-full px-4 pt-2 pb-2 mb-4">
      <div className="w-full max-w-[1200px] mx-auto flex items-center justify-between gap-3">

        {/* Left Side: Scrollable Filters (Horizontal scroll under the thumb) */}
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide py-1 flex-1">
          {/* 통합 필터 (정렬 등) 버튼 */}
          {showFilterButton && (
            <button
              onClick={onFilterClick}
              className="flex-shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold transition-all border active:scale-[0.98] bg-white text-gray-500 border-gray-200"
              aria-label="상세 필터 및 정렬"
            >
              <span>필터</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5 text-gray-400">
                <path d="m6 9 6 6 6-6" />
              </svg>
            </button>
          )}

          {/* 교과서 수록도서: 초등 1~6학년 필터 / 일반: 연령대 필터 */}
          {isTextbook ? (
            TEXTBOOK_GRADE_OPTIONS.map((option) => {
              const isSelected = option.value === "all"
                ? !selectedTag || selectedTag === "all"
                : selectedTag === option.value;
              return (
                <button
                  key={option.value}
                  onClick={() => handleTagToggle(option.value)}
                  className={`flex-shrink-0 whitespace-nowrap px-4 py-2 rounded-lg text-sm font-bold transition-all border active:scale-[0.98] ${isSelected
                    ? "bg-brand-primary text-white border-brand-primary"
                    : "bg-white text-gray-500 border-gray-200"
                    }`}
                >
                  {option.label}
                </button>
              );
            })
          ) : (
            AGE_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => handleAgeToggle(option.value)}
                className={`flex-shrink-0 whitespace-nowrap px-4 py-2 rounded-lg text-sm font-bold transition-all border active:scale-[0.98] ${selectedAge === option.value
                  ? "bg-brand-primary text-white border-brand-primary"
                  : "bg-white text-gray-500 border-gray-200"
                  }`}
              >
                {option.label}
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
