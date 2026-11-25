/**
 * Clean infinite scroll with useInfiniteQuery
 */
"use client";

import { useInfiniteQuery, InfiniteData } from "@tanstack/react-query";
import { BooksResponse } from "@/lib/types";
import { searchBooks } from "@/lib/api";

interface UseBooksParams {
  searchQuery?: string;
  ageFilter?: string;
  curationFilter?: string;
  tagFilter?: string;
  sortFilter?: string;
  limit?: number;
  initialPage?: BooksResponse;
  enabled?: boolean;
  includeLibraryInfo?: boolean;
  selectedLibrary?: string | null;
}

export function useBooks({
  searchQuery,
  ageFilter,
  curationFilter,
  tagFilter,
  sortFilter = "title",
  limit = 24,
  initialPage,
  enabled = true,
  includeLibraryInfo = false,
  selectedLibrary,
}: UseBooksParams) {
  const effectiveLibrary = (sortFilter === "callno" || sortFilter === "pangyo_callno") ? (selectedLibrary || undefined) : undefined;
  const canUseInitialData = Boolean(
    initialPage && initialPage.page === 1 && initialPage.limit === limit &&
    (!includeLibraryInfo || initialPage.data.every((b) => Array.isArray(b.library_info)))
  );
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfiniteQuery({
    queryKey: ["books-infinite", searchQuery, ageFilter, curationFilter, tagFilter, sortFilter, includeLibraryInfo, effectiveLibrary, limit],
    enabled,
    queryFn: async ({ pageParam }): Promise<BooksResponse> => {
      const page = pageParam as number;
      return searchBooks(
        searchQuery || undefined,
        ageFilter || undefined,
        undefined,
        sortFilter,
        page,
        limit,
        curationFilter || undefined,
        includeLibraryInfo,
        tagFilter || undefined,
        effectiveLibrary
      );
    },
    getNextPageParam: (lastPage) => {
      const currentPage = lastPage.page;
      const totalPages = lastPage.total_pages || 0;
      return currentPage < totalPages ? currentPage + 1 : undefined;
    },
    initialPageParam: 1,
    initialData: canUseInitialData && initialPage ? {
      pages: [initialPage],
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
