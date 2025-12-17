"use client";

import { useState, useEffect, FormEvent } from "react";
import { Search } from "lucide-react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  initialQuery?: string;
  onFilterClick: () => void;
}

export default function SearchBar({ onSearch, initialQuery = "", onFilterClick }: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);

  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query, onSearch]);

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <div className="w-full sticky top-0 z-20 bg-[#F7F7F7]/95 backdrop-blur-sm border-b border-gray-200/50 px-4 py-4 transition-all">
      <form onSubmit={handleSubmit} className="w-full max-w-[1200px] mx-auto flex gap-3">
        <div className="relative group flex-1">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="어떤 책을 찾으시나요?"
            className="w-full px-5 py-3 pl-12 bg-white text-gray-900 placeholder:text-gray-400 border border-transparent rounded-2xl shadow-[0_2px_15px_rgba(0,0,0,0.04)] focus:outline-none focus:ring-2 focus:ring-[#F59E0B]/20 focus:scale-[1.01] transition-all"
          />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5 group-focus-within:text-[#F59E0B] transition-colors" />
        </div>

        <button
          type="button"
          onClick={onFilterClick}
          className="bg-white p-3 rounded-2xl shadow-[0_2px_15px_rgba(0,0,0,0.04)] border border-transparent hover:border-gray-200 active:scale-95 transition-all text-gray-700"
          aria-label="필터 열기"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="4" x2="20" y1="21" y2="21" />
            <line x1="4" x2="20" y1="3" y2="3" />
            <line x1="4" x2="20" y1="12" y2="12" />
            <circle cx="8" cy="12" r="2" />
            <circle cx="16" cy="3" r="2" />
            <circle cx="12" cy="21" r="2" />
          </svg>
        </button>
      </form>
    </div>
  );
}
