"use client";

import { useState, useCallback } from "react";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import BookList from "@/components/BookList";
import { BooksResponse } from "@/lib/types";

import IntegratedFilterModal from "@/components/IntegratedFilterModal";

interface HomeClientProps {
    initialData: BooksResponse;
}

export default function HomeClient({ initialData }: HomeClientProps) {
    const [searchQuery, setSearchQuery] = useState("");
    const [ageFilter, setAgeFilter] = useState("");
    const [categoryFilter, setCategoryFilter] = useState("전체");
    const [sortFilter, setSortFilter] = useState("pangyo_callno");
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
    const [filterModalMode, setFilterModalMode] = useState<"integrated" | "category">("integrated");

    const handleSearch = useCallback((query: string) => {
        setSearchQuery(query);
    }, []);

    const handleAgeChange = useCallback((age: string) => {
        setAgeFilter(age);
    }, []);

    const handleCategoryChange = useCallback((category: string) => {
        setCategoryFilter(category);
    }, []);

    const handleSortChange = useCallback((sort: string) => {
        setSortFilter(sort);
    }, []);

    const openIntegratedFilter = () => {
        setFilterModalMode("integrated");
        setIsFilterModalOpen(true);
    };

    const openCategoryFilter = () => {
        setFilterModalMode("category");
        setIsFilterModalOpen(true);
    };

    return (
        <main className="min-h-screen">
            {/* Header / Logo */}
            <header className="w-full bg-white border-b border-gray-100 flex items-center justify-center py-5">
                <img
                    src="/logo.png"
                    alt="책방구"
                    className="h-12 w-auto"
                />
            </header>

            {/* 검색 바 */}
            <SearchBar
                onSearch={handleSearch}
                initialQuery={searchQuery}
                onFilterClick={openIntegratedFilter}
            />

            {/* 필터 바 (간소화) */}
            <FilterBar
                selectedAge={ageFilter}
                onAgeChange={handleAgeChange}
                selectedCategory={categoryFilter}
                onCategoryClick={openCategoryFilter}
            />

            {/* 통합 필터 모달 */}
            <IntegratedFilterModal
                isOpen={isFilterModalOpen}
                onClose={() => setIsFilterModalOpen(false)}
                mode={filterModalMode}
                searchQuery={searchQuery}
                selectedCategory={categoryFilter}
                onCategoryChange={handleCategoryChange}
                selectedAge={ageFilter}
                onAgeChange={handleAgeChange}
                selectedSort={sortFilter}
                onSortChange={handleSortChange}
            />

            {/* 책 리스트 */}
            <div className="w-full max-w-7xl mx-auto py-4 md:py-6">
                <BookList
                    searchQuery={searchQuery || undefined}
                    ageFilter={ageFilter || undefined}
                    categoryFilter={categoryFilter === "전체" ? undefined : categoryFilter}
                    sortFilter={sortFilter}
                    initialData={initialData}
                />
            </div>
        </main>
    );
}
