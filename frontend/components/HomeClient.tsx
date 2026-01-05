"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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
    const router = useRouter();
    const searchParams = useSearchParams();

    // URL에서 초기 상태 읽기
    const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || "");
    const [ageFilter, setAgeFilter] = useState(searchParams.get('age') || "");
    const [categoryFilter, setCategoryFilter] = useState(searchParams.get('category') || "전체");
    const [sortFilter, setSortFilter] = useState(searchParams.get('sort') || "pangyo_callno");
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
    const [filterModalMode, setFilterModalMode] = useState<"integrated" | "category">("integrated");
    const { user, signOut } = useAuth();

    // URL 업데이트 함수
    const updateURL = useCallback((params: Record<string, string>) => {
        const newParams = new URLSearchParams(searchParams.toString());

        Object.entries(params).forEach(([key, value]) => {
            if (value && value !== "전체") {
                newParams.set(key, value);
            } else {
                newParams.delete(key);
            }
        });

        router.push(`?${newParams.toString()}`, { scroll: false });
    }, [router, searchParams]);

    const handleSearch = useCallback((query: string) => {
        setSearchQuery(query);
        updateURL({ q: query, age: ageFilter, category: categoryFilter, sort: sortFilter });
    }, [ageFilter, categoryFilter, sortFilter, updateURL]);

    const handleAgeChange = useCallback((age: string) => {
        setAgeFilter(age);
        updateURL({ q: searchQuery, age, category: categoryFilter, sort: sortFilter });
    }, [searchQuery, categoryFilter, sortFilter, updateURL]);

    const handleCategoryChange = useCallback((category: string) => {
        setCategoryFilter(category);
        updateURL({ q: searchQuery, age: ageFilter, category, sort: sortFilter });
    }, [searchQuery, ageFilter, sortFilter, updateURL]);

    const handleSortChange = useCallback((sort: string) => {
        setSortFilter(sort);
        updateURL({ q: searchQuery, age: ageFilter, category: categoryFilter, sort });
    }, [searchQuery, ageFilter, categoryFilter, updateURL]);

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
