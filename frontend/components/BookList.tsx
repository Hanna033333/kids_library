"use client";

import { useState, useEffect } from "react";
import { Book, searchBooks, getBooks } from "@/lib/api";
import BookItem from "./BookItem";

interface BookListProps {
  searchQuery?: string;
  ageFilter?: string;
  sortFilter?: string;
}

const ITEMS_PER_PAGE = 10;

export default function BookList({ searchQuery, ageFilter, sortFilter = "pangyo_callno" }: BookListProps) {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  useEffect(() => {
    setPage(1); // 검색어나 필터 변경 시 첫 페이지로 리셋
  }, [searchQuery, ageFilter, sortFilter]);

  useEffect(() => {
    loadBooks(page);
  }, [page, searchQuery, ageFilter, sortFilter]);

  const loadBooks = async (currentPage: number) => {
    try {
      setLoading(true);
      const response = searchQuery
        ? await searchBooks(searchQuery, ageFilter || undefined, sortFilter, currentPage, ITEMS_PER_PAGE)
        : await getBooks(ageFilter || undefined, sortFilter, currentPage, ITEMS_PER_PAGE);

      setBooks(response.data);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (error) {
      console.error("Failed to load books:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages && !loading) {
      setPage(newPage);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  if (loading && books.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-500">로딩 중...</div>
      </div>
    );
  }

  if (books.length === 0) {
    return (
      <div className="flex flex-col justify-center items-center py-12">
        <p className="text-gray-500 text-lg mb-2">검색 결과가 없습니다</p>
        <p className="text-gray-400 text-sm">
          {searchQuery ? `"${searchQuery}"에 대한 결과가 없습니다` : "책을 찾을 수 없습니다"}
        </p>
      </div>
    );
  }

  // 페이지네이션 번호 생성
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 5; // 최대 표시할 페이지 번호 수

    if (totalPages <= maxVisible) {
      // 전체 페이지가 적으면 모두 표시
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // 현재 페이지 주변만 표시
      if (page <= 3) {
        // 앞부분
        for (let i = 1; i <= 5; i++) {
          pages.push(i);
        }
        pages.push("...");
        pages.push(totalPages);
      } else if (page >= totalPages - 2) {
        // 뒷부분
        pages.push(1);
        pages.push("...");
        for (let i = totalPages - 4; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        // 중간
        pages.push(1);
        pages.push("...");
        for (let i = page - 1; i <= page + 1; i++) {
          pages.push(i);
        }
        pages.push("...");
        pages.push(totalPages);
      }
    }
    return pages;
  };

  return (
    <div className="w-full">
      <div className="px-4 py-3 text-sm text-gray-600 bg-gray-50 border-b border-gray-200">
        총 {total.toLocaleString()}권 (페이지 {page} / {totalPages})
      </div>
      {/* 세로 리스트 형식 */}
      <div className="bg-white">
        {loading && books.length === 0 ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-gray-500">로딩 중...</div>
          </div>
        ) : (
          books.map((book) => (
            <BookItem key={book.id} book={book} />
          ))
        )}
      </div>
      
      {/* 페이지네이션 */}
      {totalPages > 1 && (
        <div className="px-4 py-6 bg-white border-t border-gray-200">
          <div className="flex justify-center items-center gap-2 flex-wrap">
            {/* 이전 페이지 버튼 */}
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1 || loading}
              className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              이전
            </button>

            {/* 페이지 번호 */}
            {getPageNumbers().map((pageNum, index) => {
              if (pageNum === "...") {
                return (
                  <span key={`ellipsis-${index}`} className="px-2 text-gray-400">
                    ...
                  </span>
                );
              }
              return (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum as number)}
                  disabled={loading}
                  className={`px-3 py-2 text-sm border rounded-md transition-colors ${
                    page === pageNum
                      ? "bg-blue-600 text-white border-blue-600"
                      : "border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}

            {/* 다음 페이지 버튼 */}
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages || loading}
              className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              다음
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

