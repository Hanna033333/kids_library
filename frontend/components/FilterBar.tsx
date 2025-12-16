"use client";

interface FilterBarProps {
  selectedAge: string;
  onAgeChange: (age: string) => void;
  selectedSort: string;
  onSortChange: (sort: string) => void;
}

const AGE_OPTIONS = [
  { value: "", label: "전체" },
  { value: "0-3", label: "0-3세" },
  { value: "4-7", label: "4-7세" },
  { value: "8-12", label: "8-12세" },
  { value: "13+", label: "13세+" },
];

const SORT_OPTIONS = [
  { value: "pangyo_callno", label: "청구기호순" },
  { value: "title", label: "제목순" },
];

export default function FilterBar({ selectedAge, onAgeChange, selectedSort, onSortChange }: FilterBarProps) {
  return (
    <div className="w-full px-4 py-2 mb-2">
      <div className="w-full max-w-[1200px] mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">

        {/* 연령대 필터 (Pills) */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0 scrollbar-hide">
          {AGE_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => onAgeChange(option.value)}
              className={`whitespace-nowrap px-4 py-2 rounded-full text-[13px] font-bold transition-all ${selectedAge === option.value
                ? "bg-[#F59E0B] text-white shadow-md shadow-yellow-200"
                : "bg-white text-gray-500 border border-gray-100 hover:bg-gray-50 hover:text-gray-900"
                }`}
            >
              {option.label}
            </button>
          ))}
        </div>

        {/* 정렬 필터 (Simple Text/Icon or Small Pills) */}
        <div className="flex items-center gap-2 self-end md:self-auto">
          {SORT_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => onSortChange(option.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${selectedSort === option.value
                ? "text-[#F59E0B] bg-yellow-50"
                : "text-gray-400 hover:text-gray-600"
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
