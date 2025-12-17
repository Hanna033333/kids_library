"use client";

import { useState, useEffect } from "react";
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
  showAvailableOnly?: boolean;
  initialData?: BooksResponse;
}

const ITEMS_PER_PAGE = 24; // Increased for grid layout (e.g., 4x6)

export default function BookList({
  searchQuery,
  ageFilter,
  categoryFilter,
  sortFilter = "pangyo_callno",
  showAvailableOnly = false,
  initialData,
}: BookListProps) {
  const [page, setPage] = useState(1);
  const [booksWithLoan, setBooksWithLoan] = useState<Book[]>([]);
  const [loadingLoan, setLoadingLoan] = useState(false);

  useEffect(() => {
    setPage(1);
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

  // 책 목록이 로드되면 백그라운드에서 대출 정보 조회
  useEffect(() => {
    if (books.length > 0 && !loading) {
      // 먼저 대출 정보 없이 책 표시
      setBooksWithLoan(books);

      // 백그라운드에서 대출 정보 로딩
      setLoadingLoan(true);
      const bookIds = books.map(b => b.id);

      fetchLoanStatuses(bookIds)
        .then(loanStatuses => {
          // 대출 정보를 책 데이터에 병합
          const updatedBooks = books.map(book => ({
            ...book,
            loan_status: loanStatuses[book.id] || null
          }));
          setBooksWithLoan(updatedBooks);
        })
        .catch(err => {
          console.error('Failed to fetch loan statuses:', err);
          // 실패해도 책은 그대로 표시
        })
        .finally(() => {
          setLoadingLoan(false);
        });
    } else {
      setBooksWithLoan([]);
    }
  }, [books, loading]);

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // 대출 가능 여부 필터링 (클라이언트 사이드)
  const displayedBooks = showAvailableOnly
    ? booksWithLoan.filter(book => book.loan_status?.available === true)
    : booksWithLoan;

  return (
    <div className="w-full max-w-[1200px] mx-auto px-4">
      {/* 상태 표시 (Cleaner) */}
      <div className="mb-4 px-1 flex flex-col gap-2">
        <div className="flex items-center justify-between text-sm text-gray-500 font-medium">
          <span>
            {showAvailableOnly ? (
              <>대출 가능한 책 <span className="font-bold text-green-600">{displayedBooks.length}</span>권 (전체 <span className="font-bold">{total.toLocaleString()}</span>권 중)</>
            ) : (
              <>총 <span className="font-bold">{total.toLocaleString()}</span>권</>
            )}
          </span>
        </div>
      </div>

      {/* 에러 표시 */}
      {error && (
        <div className="py-20 text-center bg-white rounded-xl shadow-sm">
          <p className="text-red-500 font-medium mb-2">데이터를 불러오지 못했습니다.</p>
          <p className="text-sm text-gray-400">{error}</p>
        </div>
      )}

      {/* 책 리스트 그리드 */}
      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
          {/* Skeleton Loading Effect can be added here, for now simple loading */}
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="aspect-[1/1.6] bg-gray-200 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : displayedBooks.length === 0 ? (
        <div className="py-32 text-center bg-white rounded-2xl border border-dashed border-gray-200">
          <div className="text-gray-400 text-lg">
            {showAvailableOnly && booksWithLoan.length > 0
              ? "대출 가능한 책이 없습니다."
              : "검색 결과가 없습니다."}
          </div>
          <div className="text-gray-300 text-sm mt-1">
            {showAvailableOnly ? "필터 조건을 변경해보세요." : "다른 검색어로 시도해보세요."}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
          {displayedBooks.map((book) => <BookItem key={book.id} book={book} />)}
        </div>
      )}

      {/* 페이지네이션 (필터링 상태에선 페이지네이션이 전체 데이터 기준이라 조금 어색할 수 있지만 유지) */}
      {!loading && !showAvailableOnly && (
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
