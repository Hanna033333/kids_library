"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import BookList from "@/components/BookList";
import { BooksResponse } from "@/lib/types";
import { useAuth } from "@/context/AuthContext";
import { LogIn, User, Search } from "lucide-react";
import Link from "next/link";
import IntegratedFilterModal from "@/components/IntegratedFilterModal";
import PageHeader from "@/components/PageHeader";
import { sendGAEvent } from "@/lib/analytics";
import UserAvatar from "@/components/UserAvatar";

interface HomeClientProps {
}

export default function HomeClient({ }: HomeClientProps) {
    const router = useRouter();
    const searchParams = useSearchParams();

    // URL에서 초기 상태 읽기 (teen → 13+ 정규화)
    const normalizeAge = (age: string) => age === "teen" ? "13+" : age;
    const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || "");
    const [ageFilter, setAgeFilter] = useState(normalizeAge(searchParams.get('age') || ""));
    const [categoryFilter, setCategoryFilter] = useState(searchParams.get('category') || "전체");
    const [curationFilter] = useState(searchParams.get('curation') || "");
    const [sortFilter, setSortFilter] = useState(searchParams.get('sort') || "pangyo_callno");
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
    const [filterModalMode, setFilterModalMode] = useState<"integrated" | "category">("integrated");
    const [isSearchVisible, setIsSearchVisible] = useState(false);
    const { user, signOut } = useAuth();

    // URL 업데이트 함수
    const updateURL = useCallback((params: Record<string, string>) => {
        // Use window.location.search to get current params without dependency
        const newParams = new URLSearchParams(window.location.search);

        Object.entries(params).forEach(([key, value]) => {
            if (value && value !== "전체") {
                newParams.set(key, value);
            } else {
                newParams.delete(key);
            }
        });

        router.push(`?${newParams.toString()}`, { scroll: false });
    }, [router]);

    const handleSearch = useCallback((query: string) => {
        setSearchQuery(query);
        sendGAEvent('search', { keyword: query });
        updateURL({ q: query, age: ageFilter, category: categoryFilter, sort: sortFilter });
    }, [ageFilter, categoryFilter, sortFilter, updateURL]);

    const handleAgeChange = useCallback((age: string) => {
        setAgeFilter(age);
        sendGAEvent('filter_change', { type: 'age', value: age });
        updateURL({ q: searchQuery, age, category: categoryFilter, sort: sortFilter });
    }, [searchQuery, categoryFilter, sortFilter, updateURL]);

    const handleCategoryChange = useCallback((category: string) => {
        setCategoryFilter(category);
        sendGAEvent('filter_change', { type: 'category', value: category });
        updateURL({ q: searchQuery, age: ageFilter, category, sort: sortFilter });
    }, [searchQuery, ageFilter, sortFilter, updateURL]);

    const handleSortChange = useCallback((sort: string) => {
        setSortFilter(sort);
        sendGAEvent('filter_change', { type: 'sort', value: sort });
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

    // URL 파라미터에 따라 동적 타이틀 결정
    const getPageTitle = () => {
        if (curationFilter === 'research-council' || curationFilter === '어린이도서연구회') return '어린이도서연구회 추천'
        if (curationFilter === 'winter-vacation' || curationFilter === '겨울방학') return '겨울방학 추천도서'
        if (curationFilter === 'caldecott') return '칼데콧 수상작'
        if (curationFilter) return curationFilter
        if (ageFilter === '0-3') return '0~3세 추천 도서'
        if (ageFilter === '4-7') return '4~7세 추천 도서'
        if (ageFilter === '8-12') return '8~12세 추천 도서'
        if (ageFilter === 'teen' || ageFilter === '13+') return '13세 이상 추천 도서'
        if (searchQuery) return '도서 검색'
        return '도서 검색'
    }

    return (
        <main className="min-h-screen">
            {/* Header */}
            <PageHeader
                title={getPageTitle()}
                backHref="/"
                rightSlot={
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setIsSearchVisible(!isSearchVisible)}
                            className="text-gray-500 hover:text-gray-900 transition-colors p-1"
                            aria-label="검색 열기"
                        >
                            <Search className="w-5 h-5" />
                        </button>
                        {user ? (
                            <button
                                onClick={() => router.push('/my-page')}
                                className="hover:text-gray-900 transition-colors p-1 flex items-center justify-center group"
                                aria-label="마이 페이지"
                            >
                                <UserAvatar user={user} size={24} className="text-gray-500 group-hover:text-gray-900 transition-colors" />
                            </button>
                        ) : (
                            <button
                                onClick={() => router.push('/auth/signup')}
                                className="hover:text-gray-900 transition-colors p-1 flex items-center justify-center group"
                                aria-label="로그인"
                            >
                                <UserAvatar user={null} size={24} className="text-gray-500 group-hover:text-gray-900 transition-colors" />
                            </button>
                        )}
                    </div>
                }
            />


            {/* 검색 바 */}
            <div className={`transition-all ${isSearchVisible ? 'block' : 'hidden'}`}>
                <SearchBar
                    onSearch={handleSearch}
                    initialQuery={searchQuery}
                />
            </div>

            {/* 필터 바 (간소화) */}
            <FilterBar
                selectedAge={ageFilter}
                onAgeChange={handleAgeChange}
                selectedCategory={categoryFilter}
                onFilterClick={openIntegratedFilter}
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
            <div className="w-full max-w-7xl mx-auto pb-4 md:pb-6 pt-0">
                <BookList
                    searchQuery={searchQuery || undefined}
                    ageFilter={ageFilter || undefined}
                    categoryFilter={categoryFilter === "전체" ? undefined : categoryFilter}
                    curationFilter={curationFilter || undefined}
                    sortFilter={sortFilter}
                />
            </div>
        </main>
    );
}
