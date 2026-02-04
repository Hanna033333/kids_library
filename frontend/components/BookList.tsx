"use client";

import { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import BookItem from "./BookItem";
import { useBooks } from "@/hooks/useBooks";
import { Book } from "@/lib/types";

const ITEMS_PER_PAGE = 24;

interface BookListProps {
  searchQuery?: string;
  ageFilter?: string;
  categoryFilter?: string;
  curationFilter?: string;
  sortFilter?: string;
  initialBooks?: Book[];
}

export default function BookList({
  searchQuery,
  ageFilter,
  categoryFilter,
  curationFilter,
  sortFilter = "pangyo_callno",
  initialBooks,
}: BookListProps) {
  const [isMobile, setIsMobile] = useState(false);
  const observerTarget = useRef<HTMLDivElement>(null);

  // Mobile detection
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Fetch data with infinite scroll
  const { books, loading, error, total, hasNextPage, isFetchingNextPage, fetchNextPage } = useBooks({
    searchQuery,
    ageFilter,
    categoryFilter,
    curationFilter,
    sortFilter,
    limit: ITEMS_PER_PAGE,
    initialBooks,
  });

  // Batch fetch loan statuses for all visible books (1 API call instead of 24)
  const bookIds = books.map(b => b.id).join(',');

  const { data: loanStatuses } = useQuery({
    queryKey: ['batch-loan-status', bookIds],
    queryFn: async () => {
      if (books.length === 0) return {};
      try {
        const { fetchLoanStatuses } = await import("@/lib/api");
        return await fetchLoanStatuses(books.map(b => b.id));
      } catch (err) {
        console.warn('Batch loan status fetch failed:', err);
        return {};
      }
    },
    enabled: books.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes cache
    retry: 1,
  });

  // Infinite scroll observer (mobile only)
  useEffect(() => {
    if (!isMobile || !hasNextPage || isFetchingNextPage) return;

    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );

    const target = observerTarget.current;
    if (target) observer.observe(target);

    return () => {
      if (target) observer.unobserve(target);
    };
  }, [isMobile, hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <div className="w-full max-w-[1200px] mx-auto px-4">
      {/* Error */}
      {error && (
        <div className="py-12 text-center">
          <p className="text-red-500 font-medium mb-2">데이터를 불러오지 못했습니다.</p>
          <p className="text-sm text-gray-400">{error}</p>
        </div>
      )}

      {/* Loading (first page only) */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
            <p className="text-gray-500 font-medium animate-pulse">도서 리스트 확인 중...</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6 w-full mt-12 opacity-50">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="aspect-[1/1.6] bg-gray-200 rounded-2xl animate-pulse" />
            ))}
          </div>
        </div>
      ) : !loading && books.length === 0 ? (
        <div className="py-32 text-center bg-white rounded-2xl border border-dashed border-gray-200">
          <div className="text-gray-400 text-lg mb-2">검색 결과가 없습니다.</div>
          <div className="text-gray-300 text-sm">다른 검색어나 필터로 시도해보세요.</div>
        </div>
      ) : (
        <>
          {/* Book grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
            {books.map((book) => (
              <div key={book.id}>
                <BookItem book={book} loanStatus={loanStatuses?.[book.id]} />
              </div>
            ))}
          </div>

          {/* Infinite scroll sentinel (mobile only) */}
          {isMobile && books.length > 0 && !error && (
            <div ref={observerTarget} className="py-8 flex justify-center">
              {isFetchingNextPage && (
                <div className="w-8 h-8 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
