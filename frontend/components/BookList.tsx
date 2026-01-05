"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import BookItem from "./BookItem";
import Pagination from "./Pagination";
import { useBooks } from "@/hooks/useBooks";
import { BooksResponse, Book } from "@/lib/types";
import { fetchLoanStatuses } from "@/lib/api";

interface BookListProps {
  searchQuery?: string;
  ageFilter?: string;
  categoryFilter?: string;
  sortFilter?: string;
  initialData?: BooksResponse;
}

const ITEMS_PER_PAGE = 24;

export default function BookList({
  searchQuery,
  ageFilter,
  categoryFilter,
  sortFilter = "pangyo_callno",
  initialData,
}: BookListProps) {
  const [page, setPage] = useState(1);
  const [allBooks, setAllBooks] = useState<Book[]>([]);
  const [booksWithLoan, setBooksWithLoan] = useState<Book[]>([]);
  const [isMobile, setIsMobile] = useState(false);
  const [isFetchingMore, setIsFetchingMore] = useState(false);
  const observerTarget = useRef<HTMLDivElement>(null);

  // Detect mobile device
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Reset when filters change
  useEffect(() => {
    setPage(1);
    setAllBooks([]);
  }, [searchQuery, ageFilter, categoryFilter, sortFilter]);

  const { books, loading, error, total, totalPages } = useBooks({
    searchQuery,
    ageFilter,
    categoryFilter,
    sortFilter,
    page,
    limit: ITEMS_PER_PAGE,
    initialData,
  });

  // Update books list (mobile: append, desktop: replace)
  useEffect(() => {
    if (!loading) {
      if (books.length > 0) {
        if (isMobile && page > 1) {
          // Mobile: append new books
          setAllBooks(prev => [...prev, ...books]);
        } else {
          // Desktop or first page: replace
          setAllBooks(books);
        }
      }
      setIsFetchingMore(false);
    }
  }, [books, loading, isMobile, page]);

  // Track which books have had their loan status fetched
  const fetchedBookIds = useRef<Set<number>>(new Set());

  // Reset fetched status when filters change
  useEffect(() => {
    fetchedBookIds.current.clear();
  }, [searchQuery, ageFilter, categoryFilter, sortFilter]);

  // Sync booksWithLoan with allBooks, preserving existing statuses
  useEffect(() => {
    setBooksWithLoan(prev => {
      const prevMap = new Map(prev.map(b => [b.id, b]));
      return allBooks.map(b => {
        const existing = prevMap.get(b.id);
        // If we have existing status, keep it. Otherwise satisfy type with null/undefined logic
        if (existing && existing.loan_status) {
          return { ...b, loan_status: existing.loan_status };
        }
        return b;
      });
    });
  }, [allBooks]);

  // Lazy load loan statuses for visible books only
  useEffect(() => {
    // Only set up observer if we have books
    if (booksWithLoan.length === 0) return;

    // Intersection Observer to detect visible books
    const observer = new IntersectionObserver(
      (entries) => {
        const visibleBookIds: number[] = [];

        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const bookId = parseInt(entry.target.getAttribute('data-book-id') || '0');
            if (bookId && !fetchedBookIds.current.has(bookId)) {
              visibleBookIds.push(bookId);
              fetchedBookIds.current.add(bookId);
            }
          }
        });

        // Fetch loan status in chunks (Progressive Rendering)
        if (visibleBookIds.length > 0) {
          const chunkSize = 6;
          for (let i = 0; i < visibleBookIds.length; i += chunkSize) {
            const chunk = visibleBookIds.slice(i, i + chunkSize);

            // Fire request for this chunk
            fetchLoanStatuses(chunk)
              .then(loanStatuses => {
                setBooksWithLoan(prevBooks =>
                  prevBooks.map(book => {
                    // Update only if this book was in the chunk
                    if (chunk.includes(book.id)) {
                      return {
                        ...book,
                        loan_status: loanStatuses[book.id] || book.loan_status || null
                      };
                    }
                    return book;
                  })
                );
              })
              .catch(err => {
                console.error('Failed to fetch loan statuses chunk:', err);
                // 에러 발생 시 UI에 표시
                setBooksWithLoan(prevBooks =>
                  prevBooks.map(book => {
                    if (chunk.includes(book.id)) {
                      return {
                        ...book,
                        loan_status: { available: null, status: "통신오류", updated_at: new Date().toISOString() }
                      };
                    }
                    return book;
                  })
                );
              });
          }
        }

      },
      {
        rootMargin: '100px', // Start loading slightly before book becomes visible
        threshold: 0.1
      }
    );

    // Observe all book items
    const bookElements = document.querySelectorAll('[data-book-id]');
    bookElements.forEach(el => observer.observe(el));

    return () => {
      observer.disconnect();
    };
    // Re-run observer when booksWithLoan actually changes LENGTH (to attach to new elements)
    // But be careful not to re-run on STATUS change alone if possible? 
    // Actually, if we use [booksWithLoan.length], we handle appends.
    // If status updates, we re-render, but observer doesn't need re-init.
    // But data-book-id elements are re-rendered.
    // It's safer to re-observe.
  }, [booksWithLoan.length]);

  // Infinite scroll for mobile
  useEffect(() => {
    if (!isMobile || loading || isFetchingMore) return;

    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && page < totalPages) {
          setIsFetchingMore(true);
          setPage(prev => prev + 1);
        }
      },
      { threshold: 0.1 }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [isMobile, loading, isFetchingMore, page, totalPages]);

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="w-full max-w-[1200px] mx-auto px-4">
      {/* Status display */}
      <div className="mb-4 px-1 flex flex-col gap-2">
        <div className="flex items-center justify-between text-sm text-gray-500 font-medium">
          <span>
            총 <span className="font-bold text-gray-900">{total.toLocaleString()}</span>권
          </span>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="py-20 text-center bg-white rounded-xl shadow-sm">
          <p className="text-red-500 font-medium mb-2">데이터를 불러오지 못했습니다.</p>
          <p className="text-sm text-gray-400">{error}</p>
        </div>
      )}

      {/* Book list grid */}
      {loading && page === 1 ? (
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
      ) : !loading && allBooks.length === 0 ? (
        <div className="py-32 text-center bg-white rounded-2xl border border-dashed border-gray-200">
          <div className="text-gray-400 text-lg">
            검색 결과가 없습니다.
          </div>
          <div className="text-gray-300 text-sm mt-1">
            다른 검색어로 시도해보세요.
          </div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
            {booksWithLoan.map((book) => (
              <div key={book.id} data-book-id={book.id}>
                <BookItem book={book} />
              </div>
            ))}
          </div>

          {/* Infinite scroll trigger for mobile */}
          {isMobile && page < totalPages && !loading && !error && (
            <div ref={observerTarget} className="py-8 flex justify-center">
              <div className="w-8 h-8 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
            </div>
          )}

          {/* Loading more indicator for mobile */}
          {isMobile && isFetchingMore && !error && (
            <div className="py-8 flex justify-center">
              <div className="flex items-center gap-2 text-gray-500">
                <div className="w-5 h-5 border-3 border-gray-300 border-t-gray-600 rounded-full animate-spin"></div>
                <span className="text-sm font-medium">더 불러오는 중...</span>
              </div>
            </div>
          )}

          {/* Retry button for mobile error */}
          {isMobile && error && (
            <div className="py-8 flex justify-center flex-col items-center gap-2">
              <p className="text-sm text-red-500">불러오기 실패</p>
              <button
                onClick={() => handlePageChange(page)} // Retry current page
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200"
              >
                다시 시도
              </button>
            </div>
          )}
        </>
      )}

      {/* Pagination for desktop only */}
      {!isMobile && !loading && booksWithLoan.length > 0 && (
        <div className="mt-12 mb-20">
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={handlePageChange}
            loading={loading}
          />
        </div>
      )}
    </div>
  );
}
