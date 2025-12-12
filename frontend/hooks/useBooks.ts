/**
 * 책 데이터 로딩 및 관리 커스텀 훅
 */
"use client";

import { useState, useEffect } from "react";
import { Book, BooksResponse } from "@/lib/types";
import { searchBooks, getBooks } from "@/lib/api";

interface UseBooksParams {
  searchQuery?: string;
  ageFilter?: string;
  sortFilter?: string;
  page: number;
  limit?: number;
}

export function useBooks({
  searchQuery,
  ageFilter,
  sortFilter = "pangyo_callno",
  page,
  limit = 10,
}: UseBooksParams) {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  useEffect(() => {
    loadBooks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, searchQuery, ageFilter, sortFilter]);

  const loadBooks = async () => {
    try {
      setLoading(true);
      setError(null);

      const response: BooksResponse = searchQuery
        ? await searchBooks(searchQuery, ageFilter || undefined, sortFilter, page, limit)
        : await getBooks(ageFilter || undefined, sortFilter, page, limit);

      setBooks(response.data);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      console.error("Failed to load books:", err);
      setError("책 목록을 불러오는데 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return {
    books,
    loading,
    error,
    total,
    totalPages,
    reload: loadBooks,
  };
}

