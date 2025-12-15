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
  { value: "13+", label: "13세 이상" },
];

const SORT_OPTIONS = [
  { value: "pangyo_callno", label: "청구기호 순" },
  { value: "title", label: "제목 순" },
];

export default function FilterBar({ selectedAge, onAgeChange, selectedSort, onSortChange }: FilterBarProps) {
  return (
    <div className="w-full bg-muted border-b border-border px-4 py-3">
      <div className="w-full max-w-4xl mx-auto space-y-3">
        {/* 연령대 필터 */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2 md:text-base">
            연령대
          </label>
          <div className="flex flex-wrap gap-2 md:gap-3">
            {AGE_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => onAgeChange(option.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${selectedAge === option.value
                    ? "bg-primary text-primary-foreground"
                    : "bg-background text-foreground border border-input hover:bg-accent"
                  }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* 정렬 필터 */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2 md:text-base">
            정렬
          </label>
          <div className="flex flex-wrap gap-2 md:gap-3">
            {SORT_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => onSortChange(option.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${selectedSort === option.value
                    ? "bg-primary text-primary-foreground"
                    : "bg-background text-foreground border border-input hover:bg-accent"
                  }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

