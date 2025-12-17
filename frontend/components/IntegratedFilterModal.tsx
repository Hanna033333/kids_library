"use client";

import { X } from "lucide-react";
import { useEffect, useState } from "react";

interface IntegratedFilterModalProps {
    isOpen: boolean;
    onClose: () => void;
    // State from parent
    selectedCategory: string;
    onCategoryChange: (cat: string) => void;
    selectedAge: string;
    onAgeChange: (age: string) => void;
    selectedSort: string;
    onSortChange: (sort: string) => void;
}

const CATEGORY_OPTIONS = [
    "전체", "동화", "외국", "자연", "전통", "과학", "사회", "만화", "소설",
    "역사", "인물", "시", "예술", "학부모", "모음", "지리"
];

const AGE_OPTIONS = [
    { value: "0-3", label: "0-3세" },
    { value: "4-7", label: "4-7세" },
    { value: "8-12", label: "8-12세" },
    { value: "13+", label: "13세+" },
];

const SORT_OPTIONS = [
    { value: "pangyo_callno", label: "청구기호순 (서가배치순)" },
    { value: "title", label: "제목순" },
];

export default function IntegratedFilterModal({
    isOpen, onClose,
    selectedCategory, onCategoryChange,
    selectedAge, onAgeChange,
    selectedSort, onSortChange
}: IntegratedFilterModalProps) {
    const [localCategory, setLocalCategory] = useState(selectedCategory);
    const [localAge, setLocalAge] = useState(selectedAge);
    const [localSort, setLocalSort] = useState(selectedSort);

    // Sync state when modal opens
    useEffect(() => {
        if (isOpen) {
            setLocalCategory(selectedCategory);
            setLocalAge(selectedAge);
            setLocalSort(selectedSort);
        }
    }, [isOpen, selectedCategory, selectedAge, selectedSort]);

    const handleApply = () => {
        onCategoryChange(localCategory);
        onAgeChange(localAge);
        onSortChange(localSort);
        onClose();
    };

    const handleAgeToggle = (ageVal: string) => {
        if (localAge === ageVal) {
            setLocalAge(""); // Toggle off
        } else {
            setLocalAge(ageVal);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="w-full md:max-w-md bg-white rounded-t-2xl md:rounded-2xl shadow-2xl max-h-[90vh] overflow-hidden flex flex-col animate-in slide-in-from-bottom md:slide-in-from-bottom-10 duration-300">

                {/* Header */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                    <h2 className="text-lg font-bold text-gray-900">검색 필터</h2>
                    <button onClick={onClose} className="p-2 -mr-2 text-gray-400 hover:text-gray-900 rounded-full hover:bg-gray-100 transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto p-5 space-y-8">

                    {/* 정렬 */}
                    <section>
                        <h3 className="text-sm font-bold text-gray-900 mb-3">정렬 기준</h3>
                        <div className="flex flex-col gap-2">
                            {SORT_OPTIONS.map((option) => (
                                <label key={option.value} className="flex items-center justify-between p-3 rounded-xl border border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors">
                                    <span className="text-[15px] font-medium text-gray-700">{option.label}</span>
                                    <input
                                        type="radio"
                                        name="sort"
                                        value={option.value}
                                        checked={localSort === option.value}
                                        onChange={(e) => setLocalSort(e.target.value)}
                                        className="w-5 h-5 text-amber-500 border-gray-300 focus:ring-amber-500"
                                    />
                                </label>
                            ))}
                        </div>
                    </section>

                    <hr className="border-gray-100" />

                    {/* 연령 */}
                    <section>
                        <h3 className="text-sm font-bold text-gray-900 mb-3">연령</h3>
                        <div className="flex flex-wrap gap-2">
                            {AGE_OPTIONS.map((option) => (
                                <button
                                    key={option.value}
                                    onClick={() => handleAgeToggle(option.value)}
                                    className={`px-4 py-2 rounded-full text-[15px] font-medium transition-all border ${localAge === option.value
                                            ? "bg-gray-900 text-white border-gray-900"
                                            : "bg-white text-gray-600 border-gray-200 hover:border-gray-300"
                                        }`}
                                >
                                    {option.label}
                                </button>
                            ))}
                        </div>
                        <p className="text-xs text-gray-400 mt-2">선택하지 않으면 전체 연령이 조회됩니다.</p>
                    </section>

                    <hr className="border-gray-100" />

                    {/* 카테고리 */}
                    <section>
                        <h3 className="text-sm font-bold text-gray-900 mb-3">카테고리</h3>
                        <div className="flex flex-wrap gap-2">
                            {CATEGORY_OPTIONS.map((cat) => (
                                <button
                                    key={cat}
                                    onClick={() => setLocalCategory(cat)}
                                    className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${localCategory === cat
                                            ? "bg-amber-100 text-amber-700 font-bold"
                                            : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                                        }`}
                                >
                                    {cat}
                                </button>
                            ))}
                        </div>
                    </section>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-100 bg-white">
                    <div className="flex gap-3">
                        <button
                            onClick={() => {
                                setLocalCategory("전체");
                                setLocalAge("");
                                setLocalSort("pangyo_callno");
                            }}
                            className="px-6 py-3.5 rounded-xl font-bold text-gray-500 hover:bg-gray-50 transition-colors"
                        >
                            초기화
                        </button>
                        <button
                            onClick={handleApply}
                            className="flex-1 px-6 py-3.5 rounded-xl bg-[#F59E0B] text-white font-bold text-base shadow-lg shadow-amber-200 active:scale-[0.98] transition-all"
                        >
                            필터 적용하기
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
