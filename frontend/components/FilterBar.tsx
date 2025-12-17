"use client";

interface FilterBarProps {
  selectedAge: string;
  onAgeChange: (age: string) => void;
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  selectedSort: string;
  onSortChange: (sort: string) => void;
  showAvailableOnly: boolean;
  onAvailabilityChange: (available: boolean) => void;
}

const AGE_OPTIONS = [
  { value: "", label: "전체 연령" },
  { value: "0-3", label: "0-3세" },
  { value: "4-7", label: "4-7세" },
  { value: "8-12", label: "8-12세" },
  { value: "13+", label: "13세+" },
];

const CATEGORY_OPTIONS = [
  "전체", "동화", "외국", "자연", "전통", "과학", "사회", "만화", "소설",
  "역사", "인물", "시", "예술", "학부모", "모음", "지리"
];

const SORT_OPTIONS = [
  { value: "pangyo_callno", label: "청구기호순" },
  { value: "title", label: "제목순" },
];

export default function FilterBar({
  selectedAge, onAgeChange,
  selectedCategory, onCategoryChange,
  selectedSort, onSortChange,
  showAvailableOnly, onAvailabilityChange
}: FilterBarProps) {
  return (
    <div className="w-full px-4 py-2 mb-2 flex flex-col gap-3">
      <div className="w-full max-w-[1200px] mx-auto flex flex-col gap-3">

        {/* 카테고리 필터 (칩) - 1열 */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4 md:mx-0 md:px-0">
          {CATEGORY_OPTIONS.map((cat) => (
            <button
              key={cat}
              onClick={() => onCategoryChange(cat)}
              className={`whitespace-nowrap px-3.5 py-1.5 rounded-full text-[13px] font-bold transition-all border ${selectedCategory === cat
                ? "bg-gray-900 text-white border-gray-900 shadow-md"
                : "bg-white text-gray-500 border-gray-200 hover:border-gray-300 hover:text-gray-900"
                }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-t border-dashed border-gray-100 pt-3">
          {/* 연령대 필터 (Pills) - 2열 */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0 scrollbar-hide -mx-4 px-4 md:mx-0 md:px-0">
            {AGE_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => onAgeChange(option.value)}
                className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-bold transition-all ${selectedAge === option.value
                  ? "bg-[#F59E0B] text-white shadow-md shadow-gray-200"
                  : "bg-white text-gray-500 border border-gray-100 hover:bg-gray-50 hover:text-gray-900"
                  }`}
              >
                {option.label}
              </button>
            ))}
          </div>

          {/* 우측 컨트롤 (정렬 + 대출가능여부) */}
          <div className="flex items-center gap-4 self-end md:self-auto">
            {/* 대출가능만 보기 토글 */}
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <div className="relative">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={showAvailableOnly}
                  onChange={(e) => onAvailabilityChange(e.target.checked)}
                />
                <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500"></div>
              </div>
              <span className={`text-sm font-bold ${showAvailableOnly ? "text-green-600" : "text-gray-400"}`}>
                대출가능만
              </span>
            </label>

            <div className="h-4 w-px bg-gray-200 mx-1"></div>

            {/* 정렬 필터 */}
            <div className="flex items-center gap-1">
              {SORT_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => onSortChange(option.value)}
                  className={`px-3 py-1.5 rounded-lg text-[13px] font-medium transition-colors ${selectedSort === option.value
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
      </div>
    </div>
  );
}
