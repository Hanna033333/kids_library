"use client";

import { useState } from "react";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import BookList from "@/components/BookList";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [ageFilter, setAgeFilter] = useState("");
  const [sortFilter, setSortFilter] = useState("pangyo_callno");

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleAgeChange = (age: string) => {
    setAgeFilter(age);
  };

  const handleSortChange = (sort: string) => {
    setSortFilter(sort);
  };

  return (
    <main className="min-h-screen bg-white">
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
        />
      </div>
    </main>
  );
}

