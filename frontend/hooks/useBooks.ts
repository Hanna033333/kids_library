/**
 * 책 데이터 로딩 및 관리 커스텀 훅
 */
"use client";

import { useQuery } from "@tanstack/react-query";
import { BooksResponse } from "@/lib/types";
import { searchBooks, getBooks } from "@/lib/api";

interface UseBooksParams {
  searchQuery?: string;
  ageFilter?: string;
  sortFilter?: string;
  page: number;
  limit?: number;
  initialData?: BooksResponse;
}

export function useBooks({
  searchQuery,
  ageFilter,
  sortFilter = "pangyo_callno",
  page,
  limit = 10,
  initialData,
}: UseBooksParams) {
  // Create a unique query key based on all parameters
  const queryKey = ["books", searchQuery, ageFilter, sortFilter, page, limit];

  const { data, isLoading, error, refetch } = useQuery({
    queryKey,
    queryFn: async (): Promise<BooksResponse> => {
      return searchQuery
        ? await searchBooks(searchQuery, ageFilter || undefined, sortFilter, page, limit)
        : await getBooks(ageFilter || undefined, sortFilter, page, limit);
    },
    // Keep data fresh for 30 seconds
    staleTime: 30 * 1000,
    // Use initialData only if provided and we are on the first page with no filters
    initialData: (searchQuery || ageFilter || page > 1) ? undefined : initialData,
  });

  return {
    books: data?.data || [],
    loading: isLoading,
    error: error ? "책 목록을 불러오는데 실패했습니다." : null,
    total: data?.total || 0,
    totalPages: data?.total_pages || 0,
    reload: refetch,
  };
}

