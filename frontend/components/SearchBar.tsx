"use client";

import { useState, useEffect, FormEvent } from "react";
import { Search } from "lucide-react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  initialQuery?: string;
}

export default function SearchBar({ onSearch, initialQuery = "" }: SearchBarProps) {
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
    <div className="w-full sticky top-0 z-20 bg-white/95 backdrop-blur-sm px-6 py-6 transition-all">
      <form onSubmit={handleSubmit} className="w-full max-w-[1200px] mx-auto flex items-center">
        <div className="flex-1 flex items-center border-b-2 border-gray-200 focus-within:border-[#F59E0B] pb-2 gap-3 relative transition-colors">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="어떤 책을 찾으시나요?"
            className="w-full bg-transparent text-xl sm:text-2xl font-bold text-gray-900 placeholder:text-gray-300 focus:outline-none pr-24 py-1"
          />

          {/* Buttons container inside input line wrapper */}
          <div className="absolute right-0 flex items-center gap-2">
            {/* Clear button */}
            {query && (
              <button
                type="button"
                onClick={() => setQuery('')}
                className="text-gray-400 hover:text-gray-600 transition-colors p-1"
                aria-label="검색어 지우기"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            )}

            {/* Primary Pill Search button */}
            <button
              type="submit"
              className="h-10 px-5 bg-[#F59E0B] active:bg-[#D97706] text-white text-sm font-bold rounded-full transition-all flex items-center justify-center shrink-0 active:scale-[0.97]"
            >
              검색
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
