/**
 * Clean infinite scroll with useInfiniteQuery
 */
"use client";

import { useInfiniteQuery, InfiniteData } from "@tanstack/react-query";
import { BooksResponse, Book } from "@/lib/types";
import { searchBooks } from "@/lib/api";

interface UseBooksParams {
  searchQuery?: string;
  ageFilter?: string;
  categoryFilter?: string;
  curationFilter?: string;
  sortFilter?: string;
  limit?: number;
  initialBooks?: Book[];
}

export function useBooks({
  searchQuery,
  ageFilter,
  categoryFilter,
  curationFilter,
  sortFilter = "pangyo_callno",
  limit = 24,
  initialBooks,
}: UseBooksParams) {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfiniteQuery({
    queryKey: ["books-infinite", searchQuery, ageFilter, categoryFilter, curationFilter, sortFilter],
    queryFn: async ({ pageParam }): Promise<BooksResponse> => {
      const page = pageParam as number;

      if (searchQuery) {
        return await searchBooks(
          searchQuery,
          ageFilter || undefined,
          categoryFilter || undefined,
          sortFilter,
          page,
          limit
        );
      }

      const { getBooksFromSupabase } = await import("@/lib/supabase-client");
      return await getBooksFromSupabase(page, limit, {
        age: ageFilter,
        category: categoryFilter,
        curation: curationFilter,
        sort: sortFilter,
      });
    },
    getNextPageParam: (lastPage, allPages) => {
      const currentPage = allPages.length;
      const totalPages = lastPage.total_pages || 0;
      return currentPage < totalPages ? currentPage + 1 : undefined;
    },
    initialPageParam: 1,
    initialData: initialBooks ? {
      pages: [{
        data: initialBooks,
        total: initialBooks.length, // approximate for initial
        page: 1,
        total_pages: 1 // fetching next page will resolve real total
      }],
      pageParams: [1]
    } as InfiniteData<BooksResponse> : undefined,
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
