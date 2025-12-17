"use client";

interface FilterBarProps {
  selectedAge: string;
  onAgeChange: (age: string) => void;
  selectedCategory: string;
  onCategoryClick: () => void; // Opens modal
  showAvailableOnly: boolean;
  onAvailabilityChange: (available: boolean) => void;
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
  showAvailableOnly, onAvailabilityChange
}: FilterBarProps) {

  const handleAgeToggle = (ageVal: string) => {
    if (selectedAge === ageVal) {
      onAgeChange(""); // Toggle off
    } else {
      onAgeChange(ageVal);
    }
  };

  return (
    <div className="w-full px-4 py-2 mb-2">
      <div className="w-full max-w-[1200px] mx-auto flex items-center gap-3 overflow-x-auto scrollbar-hide py-1">

        {/* 카테고리 버튼 (접힘 상태) */}
        <button
          onClick={onCategoryClick}
          className={`flex-shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-bold transition-all border ${selectedCategory && selectedCategory !== "전체"
              ? "bg-gray-900 text-white border-gray-900 shadow-md"
              : "bg-white text-gray-700 border-gray-200 hover:bg-gray-50"
            }`}
        >
          <span>{selectedCategory && selectedCategory !== "전체" ? selectedCategory : "카테고리"}</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={`w-3.5 h-3.5 ${selectedCategory && selectedCategory !== "전체" ? "text-gray-400" : "text-gray-400"}`}>
            <path d="m6 9 6 6 6-6" />
          </svg>
        </button>

        <div className="w-px h-6 bg-gray-200 flex-shrink-0 mx-1"></div>

        {/* 연령대 필터 (펼침 상태 + 토글) */}
        <div className="flex items-center gap-2">
          {AGE_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => handleAgeToggle(option.value)}
              className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-bold transition-all border ${selectedAge === option.value
                ? "bg-[#F59E0B] text-white border-[#F59E0B] shadow-md shadow-amber-100"
                : "bg-white text-gray-500 border-gray-200 hover:border-gray-300 hover:text-gray-700"
                }`}
            >
              {option.label}
            </button>
          ))}
        </div>

        <div className="w-px h-6 bg-gray-200 flex-shrink-0 mx-1"></div>

        {/* 대출가능 여부 */}
        <label className="flex items-center gap-2 cursor-pointer select-none flex-shrink-0 bg-white px-3 py-1.5 rounded-full border border-gray-100/50 hover:bg-gray-50 transition-colors">
          <div className="relative">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={showAvailableOnly}
              onChange={(e) => onAvailabilityChange(e.target.checked)}
            />
            <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500"></div>
          </div>
          <span className={`text-[13px] font-bold ${showAvailableOnly ? "text-green-600" : "text-gray-500"}`}>
            대출가능만
          </span>
        </label>
      </div>
    </div>
  );
}
