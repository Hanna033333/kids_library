"use client";

import { useState, useEffect } from "react";
import BookItem from "./BookItem";
import Pagination from "./Pagination";
import { useBooks } from "@/hooks/useBooks";

interface BookListProps {
  searchQuery?: string;
  ageFilter?: string;
  sortFilter?: string;
}

const ITEMS_PER_PAGE = 10;

export default function BookList({
  searchQuery,
  ageFilter,
  sortFilter = "pangyo_callno",
}: BookListProps) {
  const [page, setPage] = useState(1);

  // 검색어나 필터 변경 시 첫 페이지로 리셋
  useEffect(() => {
    setPage(1);
  }, [searchQuery, ageFilter, sortFilter]);

  // 커스텀 훅으로 데이터 로딩
  const { books, loading, error, total, totalPages } = useBooks({
    searchQuery,
    ageFilter,
    sortFilter,
    page,
    limit: ITEMS_PER_PAGE,
  });

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="w-full">
      {/* 상태 표시 */}
      <div className="px-4 py-3 text-sm text-gray-600 bg-gray-50 border-b border-gray-200">
        총 {total.toLocaleString()}권 (페이지 {page} / {totalPages})
      </div>

      {/* 에러 표시 */}
      {error && (
        <div className="px-4 py-12 text-center">
          <p className="text-red-500">{error}</p>
        </div>
      )}

      {/* 책 리스트 */}
      <div className="bg-white">
        {loading && books.length === 0 ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-gray-500">로딩 중...</div>
          </div>
        ) : books.length === 0 ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-gray-500">검색 결과가 없습니다.</div>
          </div>
        ) : (
          books.map((book) => <BookItem key={book.id} book={book} />)
        )}
      </div>

      {/* 페이지네이션 */}
      <Pagination
        currentPage={page}
        totalPages={totalPages}
        onPageChange={handlePageChange}
        loading={loading}
      />
    </div>
  );
}

