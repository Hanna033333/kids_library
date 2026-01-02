"use client";

import { useState, useCallback } from "react";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import BookList from "@/components/BookList";
import { BooksResponse } from "@/lib/types";
import { useAuth } from "@/context/AuthContext";
import { LogIn, User, LogOut, Bookmark } from "lucide-react";
import Link from "next/link";

import IntegratedFilterModal from "@/components/IntegratedFilterModal";

interface HomeClientProps {
    initialData?: BooksResponse;
}

export default function HomeClient({ initialData }: HomeClientProps) {
    const [searchQuery, setSearchQuery] = useState("");
    const [ageFilter, setAgeFilter] = useState("");
    const [categoryFilter, setCategoryFilter] = useState("전체");
    const [sortFilter, setSortFilter] = useState("pangyo_callno");
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
    const [filterModalMode, setFilterModalMode] = useState<"integrated" | "category">("integrated");
    const { user, signOut } = useAuth();

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
            <header className="w-full bg-white border-b border-gray-100 flex items-center justify-between px-6 py-4 sticky top-0 z-50">
                <div className="w-1/3"></div>
                <div className="w-1/3 flex justify-center">
                    <Link href="/" className="relative inline-flex items-center">
                        <img
                            src="/logo.png"
                            alt="책방구"
                            className="h-10 w-auto"
                        />
                        <span className="absolute top-1 -right-9 text-gray-400 text-xs font-bold leading-none italic">
                            beta
                        </span>
                    </Link>
                </div>
                <div className="w-1/3 flex justify-end items-center gap-4">
                    {user && (
                        <div className="flex items-center gap-3">
                            <Link
                                href="/my-library"
                                className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-600 flex items-center gap-1 text-sm font-medium"
                                title="내 서재"
                            >
                                <Bookmark className="w-5 h-5" />
                                <span className="hidden sm:inline">내 서재</span>
                            </Link>
                            <button
                                onClick={() => signOut()}
                                className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-600"
                                title="로그아웃"
                            >
                                <LogOut className="w-5 h-5" />
                            </button>
                        </div>
                    )}
                </div>
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
