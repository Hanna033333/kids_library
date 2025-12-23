"use client";

interface FilterBarProps {
  selectedAge: string;
  onAgeChange: (age: string) => void;
  selectedCategory: string;
  onCategoryClick: () => void; // Opens modal
}

const AGE_OPTIONS = [
  { value: "0-3", label: "0-3세" },
  { value: "4-7", label: "4-7세" },
  { value: "8-12", label: "8-12세" },
  { value: "13+", label: "13세+" },
];

export default function FilterBar({
  selectedAge, onAgeChange,
  selectedCategory, onCategoryClick,
}: FilterBarProps) {

  const handleAgeToggle = (ageVal: string) => {
    if (selectedAge === ageVal) {
      onAgeChange(""); // Toggle off
    } else {
      onAgeChange(ageVal);
    }
  };

  return (
    <div className="w-full px-4 pb-2 mb-2">
      <div className="w-full max-w-[1200px] mx-auto">

        {/* Scrollable Filters */}
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide py-1">
          {/* 카테고리 버튼 */}
          <button
            onClick={onCategoryClick}
            className={`flex-shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-bold transition-all border ${selectedCategory && selectedCategory !== "전체"
              ? "bg-gray-900 text-white border-gray-900 shadow-md shadow-gray-200"
              : "bg-white text-gray-500 border-gray-200 hover:border-gray-300 hover:text-gray-900"
              }`}
          >
            <span>{selectedCategory && selectedCategory !== "전체" ? selectedCategory : "카테고리"}</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={`w-3.5 h-3.5 ${selectedCategory && selectedCategory !== "전체" ? "text-gray-400" : "text-gray-400"}`}>
              <path d="m6 9 6 6 6-6" />
            </svg>
          </button>

          {/* 연령대 필터 */}
          {AGE_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => handleAgeToggle(option.value)}
              className={`flex-shrink-0 whitespace-nowrap px-4 py-2 rounded-lg text-sm font-bold transition-all border ${selectedAge === option.value
                ? "bg-[#F59E0B] text-white border-[#F59E0B] shadow-md shadow-gray-200"
                : "bg-white text-gray-500 border-gray-200 hover:border-gray-300 hover:text-gray-900"
                }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
