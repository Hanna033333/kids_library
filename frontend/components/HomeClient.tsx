"use client";

import { useState, useCallback } from "react";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import BookList from "@/components/BookList";
import { BooksResponse } from "@/lib/types";

interface HomeClientProps {
    initialData: BooksResponse;
}

export default function HomeClient({ initialData }: HomeClientProps) {
    const [searchQuery, setSearchQuery] = useState("");
    const [ageFilter, setAgeFilter] = useState("");
    const [sortFilter, setSortFilter] = useState("pangyo_callno");

    const handleSearch = useCallback((query: string) => {
        setSearchQuery(query);
    }, []);

    const handleAgeChange = useCallback((age: string) => {
        setAgeFilter(age);
    }, []);

    const handleSortChange = useCallback((sort: string) => {
        setSortFilter(sort);
    }, []);

    return (
        <main className="min-h-screen">
            {/* 검색 바 */}
            <SearchBar onSearch={handleSearch} initialQuery={searchQuery} />

            {/* 필터 바 */}
            <FilterBar
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
                    sortFilter={sortFilter}
                    initialData={initialData}
                />
            </div>
        </main>
    );
}
