"use client";

import { useState, useEffect, FormEvent } from "react";
import { Search, X } from "lucide-react";

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
        <div className="flex-1 flex items-center border-b-2 border-gray-200 focus-within:border-gray-900 pb-2 gap-3 relative transition-colors">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="어떤 책을 찾으시나요?"
            className="w-full bg-transparent text-xl sm:text-2xl font-bold text-gray-900 placeholder:text-gray-300 focus:outline-none pr-20 py-1"
          />

          {/* Buttons container inside input line wrapper */}
          <div className="absolute right-0 flex items-center gap-1.5">
            {/* Clear button */}
            {query && (
              <button
                type="button"
                onClick={() => setQuery('')}
                className="text-gray-400 hover:text-gray-600 transition-colors p-1.5 rounded-full hover:bg-gray-100"
                aria-label="검색어 지우기"
              >
                <X className="w-4 h-4 text-gray-500" />
              </button>
            )}

            {/* Minimal Search Button */}
            <button
              type="submit"
              className="p-1.5 text-gray-700 hover:text-gray-900 active:text-gray-900 transition-colors flex items-center justify-center shrink-0 active:scale-95"
              aria-label="검색"
            >
              <Search className="w-5 h-5 sm:w-6 sm:h-6" />
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
