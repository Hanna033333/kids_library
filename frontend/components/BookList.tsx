"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import BookItem from "./BookItem";
import { useBooks } from "@/hooks/useBooks";
import { Book } from "@/lib/types";
import { Spinner } from "@/components/ui/Spinner";
import { PageLoader } from "@/components/ui/PageLoader";
import { useLibrary } from "@/context/LibraryContext";
import LibrarySelector from "@/components/LibrarySelector";
import { sendGAEvent } from "@/lib/analytics";
import { useAuth } from "@/context/AuthContext";
import LoginPromptModal from "@/components/ui/LoginPromptModal";
import { useRouter } from "next/navigation";

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
  const router = useRouter();
  const { user } = useAuth();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const { selectedLibrary } = useLibrary();
  const [isMobile, setIsMobile] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const observerTarget = useRef<HTMLDivElement>(null);

  // Mobile detection & mount flag
  useEffect(() => {
    setIsMounted(true);
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const isSearchWaitingState = !searchQuery && !ageFilter && (!categoryFilter || categoryFilter === "전체") && !curationFilter;

  // Fetch data with infinite scroll
  const { books, loading, error, total, hasNextPage, isFetchingNextPage, fetchNextPage } = useBooks({
    searchQuery,
    ageFilter,
    categoryFilter,
    curationFilter,
    sortFilter,
    limit: ITEMS_PER_PAGE,
    initialBooks,
    enabled: !isSearchWaitingState,
    includeLibraryInfo: !!user,
  });

  // 검색 대기 중 인기 도서 추천 쿼리
  const { data: searchWaitingRecommendedBooks = [], isLoading: isSearchWaitingRecommendedLoading } = useQuery<Book[]>({
    queryKey: ['search-waiting-recommended-books', !!user],
    queryFn: async () => {
      const { getPopularBooksOverall } = await import("@/lib/home-api");
      return getPopularBooksOverall(8, undefined, !!user);
    },
    enabled: isSearchWaitingState && isMounted,
    staleTime: 5 * 60 * 1000,
  });

  // 연령별 및 주요 큐레이션 홈 코너 추천도서 (AI 큐레이션 순 제외, 일반 필터 상태에서만 사용)
  // useQuery로 캐시화 → 상세페이지 다녀와도 캐시에서 즉시 복원 → 정렬 깜빡임 제거
  const shouldFetchRecommended = !!(
    (ageFilter || ['caldecott', '어린이도서연구회', 'research-council', '겨울방학', 'winter-vacation'].includes(curationFilter || "")) &&
    !searchQuery &&
    sortFilter === "pangyo_callno" &&
    (!categoryFilter || categoryFilter === "전체")
  );

  const { data: recommendedBooks = [], isLoading: isRecommendedLoading } = useQuery<Book[]>({
    queryKey: ['recommended-books', ageFilter, curationFilter, !!user],
    queryFn: async () => {
      if (ageFilter) {
        const { getBooksByAge } = await import("@/lib/home-api");
        return getBooksByAge(ageFilter, 7, undefined, !!user);
      }
      if (curationFilter === "caldecott") {
        const { getCaldecottBooks } = await import("@/lib/caldecott-api");
        const books = await getCaldecottBooks(undefined, !!user);
        return books.slice(0, 7);
      }
      if (curationFilter === "어린이도서연구회" || curationFilter === "research-council") {
        const { getResearchCouncilBooks } = await import("@/lib/home-api");
        return getResearchCouncilBooks(7, undefined, !!user);
      }
      if (curationFilter === "겨울방학" || curationFilter === "winter-vacation") {
        const { getWinterBooks } = await import("@/lib/home-api");
        return getWinterBooks(7, undefined, !!user);
      }
      return [];
    },
    enabled: shouldFetchRecommended && isMounted,
    staleTime: 5 * 60 * 1000, // 5분 캐시
    gcTime: 10 * 60 * 1000,   // 10분 캐시 유지
  });

  // 서버(page.tsx)에서 initialBooks를 받았거나, 추천 도서가 준비된 경우 병합 적용
  // 그렇지 않으면 books 그대로 사용
  const displayBooks = useMemo(() => {
    if (!shouldFetchRecommended || recommendedBooks.length === 0) return books;

    const recIds = new Set(recommendedBooks.map(b => b.id));
    const filteredMainBooks = books.filter(b => !recIds.has(b.id));

    return [...recommendedBooks, ...filteredMainBooks];
  }, [books, recommendedBooks, shouldFetchRecommended]);

  // SSR initialBooks가 없을 때만 추천 도서 로딩을 대기하여 첫 로드 레이아웃 흔들림 방지 및 SSR 성능 보존
  const isListLoading = !isMounted || (isSearchWaitingState
    ? isSearchWaitingRecommendedLoading
    : (loading || (!initialBooks && shouldFetchRecommended && isRecommendedLoading)));

  // 폴백 추천 도서 활성화 조건
  const isFallbackEnabled = isMounted && !isListLoading && displayBooks.length === 0 && !isSearchWaitingState;


  // 폴백 추천 도서 fetch 쿼리
  const { data: fallbackBooks = [] } = useQuery<Book[]>({
    queryKey: ['fallback-books', ageFilter, searchQuery, !!user],
    queryFn: async () => {
      if (ageFilter) {
        const { getPopularBooksByAge } = await import("@/lib/home-api");
        return getPopularBooksByAge(ageFilter, 8, undefined, !!user);
      } else {
        const { getPopularBooksOverall } = await import("@/lib/home-api");
        return getPopularBooksOverall(8, undefined, !!user);
      }
    },
    enabled: isFallbackEnabled,
    staleTime: 5 * 60 * 1000, // 5분 캐싱
  });

  // Batch fetch loan statuses for all visible books (including fallback books when list is empty)
  const visibleBooksForLoan = displayBooks.length > 0 
    ? displayBooks 
    : isSearchWaitingState 
      ? searchWaitingRecommendedBooks 
      : fallbackBooks;
  const bookIds = visibleBooksForLoan.map(b => b.id).join(',');

  const { data: loanStatuses } = useQuery({
    queryKey: ['batch-loan-status', bookIds, selectedLibrary],
    queryFn: async () => {
      if (visibleBooksForLoan.length === 0) return {};
      try {
        const { fetchLoanStatuses } = await import("@/lib/api");
        return await fetchLoanStatuses(visibleBooksForLoan.map(b => b.id), selectedLibrary);
      } catch (err) {
        console.warn('Batch loan status fetch failed:', err);
        throw err;
      }
    },
    enabled: visibleBooksForLoan.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes cache
    retry: 1,
    placeholderData: keepPreviousData,
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

  // Track no results
  useEffect(() => {
    if (!isListLoading && books.length === 0 && (searchQuery || ageFilter || categoryFilter || curationFilter)) {
      sendGAEvent('search_no_results', { 
        keyword: searchQuery,
        age: ageFilter,
        category: categoryFilter,
        curation: curationFilter
      });
    }
  }, [isListLoading, books.length, searchQuery, ageFilter, categoryFilter, curationFilter]);

  if (error) {
    return (
      <div className="w-full px-4">
        <div className="w-full max-w-[1200px] mx-auto py-12 text-center">
          <p className="text-red-500 font-medium mb-2">데이터를 불러오지 못했습니다.</p>
          <p className="text-sm text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full px-4">
      <div className="w-full max-w-[1200px] mx-auto">
        {!isSearchWaitingState && isMounted && (
          <div className="flex justify-end mt-0 mb-8 px-2">
            {user ? (
              <LibrarySelector />
            ) : (
              <button
                onClick={() => setIsLoginModalOpen(true)}
                className="text-sm sm:text-base font-semibold text-gray-700 active:text-gray-900 transition-colors underline underline-offset-2 py-2 px-1"
              >
                <span>내 도서관 대출 정보 확인</span>
              </button>
            )}
          </div>
        )}
        {/* Loading (first page only) */}
        {isListLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6 mt-4">
            {Array.from({ length: 12 }).map((_, i) => (
              <div key={i} className="flex flex-col bg-white rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-gray-100 overflow-hidden h-[320px] animate-pulse">
                <div className="w-full aspect-[1/1.1] bg-gray-100"></div>
                <div className="p-4 space-y-3 flex-1 flex flex-col">
                  <div className="h-4 bg-gray-100 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-100 rounded w-1/2"></div>
                  <div className="mt-auto h-3 bg-gray-100 rounded w-1/3"></div>
                </div>
              </div>
            ))}
          </div>
        ) : isSearchWaitingState ? (
          /* 검색 대기 상태 UI */
          <div className="space-y-8 w-full mt-4">
            {searchWaitingRecommendedBooks.length > 0 && (
              <div className="p-6 bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)]">
                {/* 2단 타이틀 구조 (서브 타이틀 위, 메인 타이틀 아래) */}
                <div className="mb-6">
                  <span className="text-[13px] text-gray-500 font-semibold block mb-1">
                    가장 많이 찾는 그림책
                  </span>
                  <h3 className="text-lg sm:text-xl font-bold text-gray-900 leading-tight">
                    인기 추천 도서
                  </h3>
                </div>

                {/* 도서 그리드 */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
                  {searchWaitingRecommendedBooks.map((book) => (
                    <div key={book.id}>
                      <BookItem book={book} loanStatus={loanStatuses?.[book.id]} />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : !isListLoading && displayBooks.length === 0 ? (
          <div className="space-y-8 w-full">
            {/* Empty State Box - Level 1 shadow, no borders */}
            <div className="py-16 text-center bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] flex flex-col items-center justify-center">
              <div className="text-gray-600 font-bold text-lg mb-1">검색 결과가 없습니다.</div>
              <div className="text-gray-400 text-sm">다른 검색어나 필터로 시도해보세요.</div>
            </div>

            {/* Fallback Recommendation Box - Level 1 shadow, no borders */}
            {fallbackBooks.length > 0 && (
              <div className="p-6 bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)]">
                {/* 2단 타이틀 구조 (서브 타이틀 위, 메인 타이틀 아래) */}
                <div className="mb-6">
                  <span className="text-[13px] text-gray-500 font-semibold block mb-1">
                    조건에 맞는 책이 없지만 이 책은 어떨까요?
                  </span>
                  <h3 className="text-lg sm:text-xl font-bold text-gray-900 leading-tight">
                    {ageFilter ? `${ageFilter}세 추천 도서` : "인기 도서 추천"}
                  </h3>
                </div>

                {/* 도서 그리드 */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
                  {fallbackBooks.map((book) => (
                    <div key={book.id}>
                      <BookItem book={book} loanStatus={loanStatuses?.[book.id]} />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <>
            {/* Book grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
              {displayBooks.map((book) => (
                <div key={book.id}>
                  <BookItem book={book} loanStatus={loanStatuses?.[book.id]} />
                </div>
              ))}
            </div>

            {/* Infinite scroll sentinel (mobile only) */}
            {isMobile && displayBooks.length > 0 && !error && (
              <div ref={observerTarget} className="py-8 flex justify-center">
                {isFetchingNextPage && (
                  <Spinner size="md" variant="primary" />
                )}
              </div>
            )}
          </>
        )}
        <LoginPromptModal
          isOpen={isLoginModalOpen}
          onClose={() => setIsLoginModalOpen(false)}
          title="좋은 책, 놓치지 않게!"
          description="자주 가는 도서관을 등록하고 실시간 대출 상태와 청구기호를 바로 확인해보세요."
        />
      </div>
    </div>
  );
}
