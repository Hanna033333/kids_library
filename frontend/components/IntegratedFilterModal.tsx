"use client";

import { X } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";

interface IntegratedFilterModalProps {
    isOpen: boolean;
    onClose: () => void;
    selectedAge: string;
    onAgeChange: (age: string) => void;
    selectedSort: string;
    onSortChange: (sort: string) => void;
}

const AGE_OPTIONS = [
    { value: "0-3", label: "0~3세" },
    { value: "4-7", label: "4~7세" },
    { value: "8-12", label: "8~12세" },
];

const SORT_OPTIONS = [
    { value: "pangyo_callno", label: "청구기호순" },
    { value: "title", label: "제목순" },
];

export default function IntegratedFilterModal({
    isOpen, onClose,
    selectedAge, onAgeChange,
    selectedSort, onSortChange
}: IntegratedFilterModalProps) {
    const normalizeAge = (age: string) => age === "teen" ? "13+" : age;
    const [localAge, setLocalAge] = useState(normalizeAge(selectedAge));
    const [localSort, setLocalSort] = useState(selectedSort);

    // Sync state when modal opens
    useEffect(() => {
        if (isOpen) {
            setLocalAge(normalizeAge(selectedAge));
            setLocalSort(selectedSort);
        }
    }, [isOpen, selectedAge, selectedSort]);

    const handleApply = () => {
        onAgeChange(localAge);
        onSortChange(localSort);
        onClose();
    };

    const handleAgeToggle = (ageVal: string) => {
        if (localAge === ageVal) setLocalAge("");
        else setLocalAge(ageVal);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="w-full md:max-w-md bg-white rounded-t-lg md:rounded-lg shadow-2xl max-h-[90vh] overflow-hidden flex flex-col animate-in slide-in-from-bottom md:slide-in-from-bottom-10 duration-300">

                {/* Header */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                    <h2 className="text-lg font-bold text-gray-900">검색 필터</h2>
                    <button onClick={onClose} className="p-2 -mr-2 text-gray-400 rounded-lg transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto p-5 space-y-8">

                    {/* 연령 */}
                    <section>
                        <h3 className="text-sm font-bold text-gray-900 mb-3">연령</h3>
                        <div className="flex flex-wrap gap-2">
                            {AGE_OPTIONS.map((option) => (
                                <button
                                    key={option.value}
                                    onClick={() => handleAgeToggle(option.value)}
                                    className={`px-4 py-2 rounded-lg text-[15px] font-medium transition-all duration-200 border ${localAge === option.value
                                        ? "bg-brand-primary text-white border-brand-primary shadow-md shadow-gray-200 transform scale-[1.02]"
                                        : "bg-white text-gray-600 border-gray-200"
                                        }`}
                                >
                                    {option.label}
                                </button>
                            ))}
                        </div>
                        <p className="text-xs text-gray-400 mt-2 ml-1">선택하지 않으면 전체 연령이 조회됩니다.</p>
                    </section>

                    <hr className="border-gray-100" />

                    {/* 정렬 */}
                    <section>
                        <h3 className="text-sm font-bold text-gray-900 mb-3">정렬 기준</h3>
                        <div className="flex gap-3">
                            {SORT_OPTIONS.map((option) => (
                                <button
                                    key={option.value}
                                    onClick={() => setLocalSort(option.value)}
                                    className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg border font-medium transition-all duration-200 ${localSort === option.value
                                        ? "bg-brand-primary border-brand-primary text-white shadow-md shadow-gray-200"
                                        : "bg-white border-gray-200 text-gray-600"
                                        }`}
                                >
                                    {option.label}
                                </button>
                            ))}
                        </div>
                    </section>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-100 bg-white">
                    <div className="flex gap-3">
                        <Button
                            onClick={() => {
                                setLocalAge("");
                                setLocalSort("pangyo_callno");
                            }}
                            variant="secondary"
                            size="lg"
                            className="px-6"
                        >
                            초기화
                        </Button>
                        <Button
                            onClick={handleApply}
                            variant="primary"
                            size="lg"
                            className="flex-1"
                        >
                            필터 적용하기
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}

