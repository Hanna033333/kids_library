/**
 * Clean infinite scroll with useInfiniteQuery
 */
"use client";

import { useInfiniteQuery } from "@tanstack/react-query";
import { BooksResponse } from "@/lib/types";
import { searchBooks } from "@/lib/api";

interface UseBooksParams {
  searchQuery?: string;
  ageFilter?: string;
  categoryFilter?: string;
  sortFilter?: string;
  limit?: number;
}

export function useBooks({
  searchQuery,
  ageFilter,
  categoryFilter,
  sortFilter = "pangyo_callno",
  limit = 24,
}: UseBooksParams) {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfiniteQuery({
    queryKey: ["books-infinite", searchQuery, ageFilter, categoryFilter, sortFilter],
    queryFn: async ({ pageParam = 1 }): Promise<BooksResponse> => {
      if (searchQuery) {
        return await searchBooks(
          searchQuery,
          ageFilter || undefined,
          categoryFilter || undefined,
          sortFilter,
          pageParam,
          limit
        );
      }

      const { getBooksFromSupabase } = await import("@/lib/supabase-client");
      return await getBooksFromSupabase(pageParam, limit, {
        age: ageFilter,
        category: categoryFilter,
        sort: sortFilter,
      });
    },
    getNextPageParam: (lastPage, allPages) => {
      const currentPage = allPages.length;
      const totalPages = lastPage.total_pages || 0;
      return currentPage < totalPages ? currentPage + 1 : undefined;
    },
    initialPageParam: 1,
    staleTime: 30 * 1000,
  });

  const allBooks = data?.pages.flatMap((page) => page.data) || [];
  const total = data?.pages[0]?.total || 0;

  return {
    books: allBooks,
    loading: isLoading,
    error: error ? "책 목록을 불러오는데 실패했습니다." : null,
    total,
    hasNextPage: hasNextPage ?? false,
    isFetchingNextPage,
    fetchNextPage,
  };
}
