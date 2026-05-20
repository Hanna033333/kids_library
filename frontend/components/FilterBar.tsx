import { Share2 } from "lucide-react";

interface FilterBarProps {
  selectedAge: string;
  onAgeChange: (age: string) => void;
  selectedCategory: string;
  onFilterClick: () => void;
  showFilterButton?: boolean;
  onShareClick?: () => void;
  showShareButton?: boolean;
}

const AGE_OPTIONS = [
  { value: "0-3", label: "0~3세" },
  { value: "4-7", label: "4~7세" },
  { value: "8-12", label: "8~12세" },
];

export default function FilterBar({
  selectedAge, onAgeChange,
  selectedCategory, onFilterClick,
  showFilterButton = true,
  onShareClick,
  showShareButton = false
}: FilterBarProps) {

  const handleAgeToggle = (ageVal: string) => {
    if (selectedAge === ageVal) {
      onAgeChange(""); // Toggle off
    } else {
      onAgeChange(ageVal);
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
              className={`flex-shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold transition-all border active:scale-[0.98] ${selectedCategory && selectedCategory !== "전체"
                ? "bg-gray-900 text-white border-gray-900"
                : "bg-white text-gray-500 border-gray-200"
                }`}
              aria-label="상세 필터 및 정렬"
            >
              <span>{selectedCategory && selectedCategory !== "전체" ? selectedCategory : "필터"}</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5 text-gray-400">
                <path d="m6 9 6 6 6-6" />
              </svg>
            </button>
          )}

          {/* 연령대 필터 */}
          {AGE_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => handleAgeToggle(option.value)}
              className={`flex-shrink-0 whitespace-nowrap px-4 py-2 rounded-lg text-sm font-bold transition-all border active:scale-[0.98] ${selectedAge === option.value
                ? "bg-[#F59E0B] text-white border-[#F59E0B]"
                : "bg-white text-gray-500 border-gray-200"
                }`}
            >
              {option.label}
            </button>
          ))}
        </div>

        {/* Right Side: Sticky, space-saving Share Button (Circular Action Button) */}
        {showShareButton && onShareClick && (
          <button
            onClick={onShareClick}
            className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full border border-gray-200 bg-white text-gray-500 active:scale-[0.95] transition-transform cursor-pointer"
            aria-label="공유하기"
            title="공유하기"
          >
            <Share2 className="w-[18px] h-[18px] text-gray-500" />
          </button>
        )}
      </div>
    </div>
  );
}
