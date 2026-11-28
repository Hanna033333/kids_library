"use client";

import { useState, useEffect, useRef, useMemo, useCallback, type ReactNode } from "react";
import { useQuery, useQueryClient, keepPreviousData } from "@tanstack/react-query";
import BookItem from "./BookItem";
import { useBooks } from "@/hooks/useBooks";
import { Book, BooksResponse } from "@/lib/types";
import { Spinner } from "@/components/ui/Spinner";
import { PageLoader } from "@/components/ui/PageLoader";
import { useLibrary, getStoredPreferredLibrary } from "@/context/LibraryContext";
import LibrarySelector from "@/components/LibrarySelector";
import { sendGAEvent } from "@/lib/analytics";
import { useAuth } from "@/context/AuthContext";
import LoginPromptModal from "@/components/ui/LoginPromptModal";
import { useRouter } from "next/navigation";
import { MapPin, ChevronDown, Info } from "lucide-react";
import { supabase } from "@/lib/supabase";
import { saveBook, unsaveBook, getSavedBookIds } from "@/lib/supabase-api";

const ITEMS_PER_PAGE = 24;

const AGE_LABELS: Record<string, string> = {
  '0-3': '0~3세',
  '4-7': '4~7세',
  '8-12': '8~12세',
  '13+': '13세 이상',
};

interface BookListProps {
  searchQuery?: string;
  ageFilter?: string;
  curationFilter?: string;
  curationTitle?: string;
  tagFilter?: string;
  sortFilter?: string;
  initialPage?: BooksResponse;
  filterBar?: ReactNode;
  toolbarRightSlot?: ReactNode;
}

export default function BookList({
  searchQuery,
  ageFilter,
  curationFilter,
  curationTitle,
  tagFilter,
  sortFilter = "title",
  initialPage,
  filterBar,
  toolbarRightSlot,
}: BookListProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [shouldAutoOpenLibrary, setShouldAutoOpenLibrary] = useState(false);
  const [savedBookIds, setSavedBookIds] = useState<Set<number>>(new Set());
  const { selectedLibrary, selectedLibraryCode } = useLibrary();
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

  // React Query를 통해 저장된 책 ID 목록 관리 (전역 캐시 동기화)
  const { data: remoteSavedBookIds } = useQuery<number[]>({
    queryKey: ['saved-book-ids', user?.id],
    queryFn: () => (user?.id ? getSavedBookIds(supabase, user.id) : Promise.resolve([])),
    enabled: !!user?.id,
    staleTime: 60 * 1000,
  });

  // 원격 캐시 데이터가 갱신되면 로컬 상태 동기화
  useEffect(() => {
    if (!user?.id) {
      setSavedBookIds((prev) => (prev.size === 0 ? prev : new Set()));
    } else if (remoteSavedBookIds) {
      setSavedBookIds(new Set(remoteSavedBookIds));
    }
  }, [user?.id, remoteSavedBookIds]);

  // 로그인 유저의 찜 목록 로드 및 로그인 복귀 후 pendingAction 자동 처리
  useEffect(() => {
    const userId = user?.id;
    if (!userId) {
      setSavedBookIds((prev) => (prev.size === 0 ? prev : new Set()));
      return;
    }

    let isCancelled = false;
    const initUserActions = async () => {
      try {
        const ids = await getSavedBookIds(supabase, userId);
        if (isCancelled) return;
        const idSet = new Set<number>(ids);

        if (typeof window !== "undefined") {
          const pendingAction = sessionStorage.getItem("pendingAction");
          const isNewSignupModalOpening = sessionStorage.getItem("showSignupComplete") === "true";

          if (pendingAction === "open_library_selector") {
            sessionStorage.removeItem("pendingAction");
            sessionStorage.removeItem("returnUrl");
            // 신규 가입 모달이 동시에 뜨거나 이미 선호 도서관이 설정된 경우 중복 바텀시트 오픈 방지
            const hasPreferredLibrary = Boolean(selectedLibrary || getStoredPreferredLibrary());
            if (!isNewSignupModalOpening && !hasPreferredLibrary) {
              setShouldAutoOpenLibrary(true);
            }
          } else if (pendingAction && pendingAction.startsWith("like_book_")) {
            const targetBookId = Number(pendingAction.replace("like_book_", ""));
            sessionStorage.removeItem("pendingAction");
            sessionStorage.removeItem("returnUrl");
            if (targetBookId && !idSet.has(targetBookId)) {
              try {
                await saveBook(supabase, userId, targetBookId);
                idSet.add(targetBookId);
                queryClient.setQueryData<number[]>(['saved-book-ids', userId], Array.from(idSet));
                queryClient.invalidateQueries({ queryKey: ['saved-books', userId] });
              } catch (err) {
                console.error("Failed auto save from list:", err);
              }
            }
          }
        }

        if (!isCancelled) {
          setSavedBookIds(new Set(idSet));
        }
      } catch (err) {
        console.error("Failed to fetch saved book ids:", err);
      }
    };

    initUserActions();
    return () => {
      isCancelled = true;
    };
  }, [user?.id, queryClient]);

  const handleToggleBookSave = useCallback(async (book: Book) => {
    if (!user) {
      if (typeof window !== "undefined") {
        sessionStorage.setItem("returnUrl", window.location.pathname + window.location.search);
        sessionStorage.setItem("pendingAction", `like_book_${book.id}`);
      }
      sendGAEvent("click_bookmark_unauth", { book_id: book.id, source: "book_list" });
      setIsLoginModalOpen(true);
      return;
    }

    const currentlySaved = savedBookIds.has(book.id);
    const nextSavedIds = new Set(savedBookIds);
    if (currentlySaved) {
      nextSavedIds.delete(book.id);
    } else {
      nextSavedIds.add(book.id);
    }

    // 낙관적 업데이트: 로컬 state와 React Query 캐시 동시 갱신
    setSavedBookIds(nextSavedIds);
    queryClient.setQueryData<number[]>(['saved-book-ids', user.id], Array.from(nextSavedIds));

    try {
      if (currentlySaved) {
        await unsaveBook(supabase, user.id, book.id);
      } else {
        await saveBook(supabase, user.id, book.id);
      }
      queryClient.invalidateQueries({ queryKey: ['saved-books', user.id] });
      queryClient.invalidateQueries({ queryKey: ['saved-book-ids', user.id] });
      sendGAEvent("toggle_save_book", {
        book_id: book.id,
        book_title: book.title,
        state: currentlySaved ? "unsave" : "save",
        source: "book_list",
      });
    } catch (err) {
      console.error("Failed to toggle save in list:", err);
      // 실패 시 롤백
      setSavedBookIds((prev) => {
        const rollback = new Set(prev);
        if (currentlySaved) rollback.add(book.id);
        else rollback.delete(book.id);
        return rollback;
      });
      queryClient.invalidateQueries({ queryKey: ['saved-book-ids', user.id] });
    }
  }, [user, savedBookIds, queryClient]);

  const isSearchWaitingState = !searchQuery && !ageFilter && !curationFilter && !tagFilter;

  // Fetch data with infinite scroll
  const { books, loading, error, total, hasNextPage, isFetchingNextPage, fetchNextPage } = useBooks({
    searchQuery,
    ageFilter,
    curationFilter,
    tagFilter,
    sortFilter,
    limit: ITEMS_PER_PAGE,
    initialPage,
    enabled: !isSearchWaitingState,
    includeLibraryInfo: !!user,
    selectedLibrary,
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

  // 연령별 및 주요 큐레이션/AI 큐레이션 추천도서 최상단 우선 고정 (Visual Continuity 보장)
  // useQuery로 캐시화 → 상세페이지 다녀와도 캐시에서 즉시 복원 → 정렬 깜빡임 제거
  const shouldFetchRecommended = !!(
    (ageFilter || curationFilter || tagFilter) &&
    !searchQuery
  );

  const { data: recommendedBooks = [], isLoading: isRecommendedLoading } = useQuery<Book[]>({
    queryKey: ['recommended-books', ageFilter, curationFilter, tagFilter, sortFilter, !!user],
    queryFn: async () => {
      const { isBookMatchingAge } = await import("@/lib/utils/age");
      const filterByAgeIfSet = (list: Book[], maxCount: number = 7) =>
        ageFilter ? list.filter(b => isBookMatchingAge(b, ageFilter)).slice(0, maxCount) : list.slice(0, maxCount);

      // 1. 교과서 수록도서 (학년 태그 지원)
      if (curationFilter === '교과서수록' || curationFilter === 'textbook') {
        const { getTextbookBooks } = await import("@/lib/home-api");
        return getTextbookBooks(tagFilter, 8, undefined, !!user);
      }
      // 2. 칼데콧 수상작 (홈 화면과 동일한 풀 + 연령 필터 일치 시 해당 연령만 최상단 고정)
      if (curationFilter === "caldecott") {
        const { getCaldecottBooks } = await import("@/lib/caldecott-api");
        const books = await getCaldecottBooks(undefined, !!user);
        return filterByAgeIfSet(books, 7);
      }
      // 3. 어린이도서연구회 (홈 화면과 동일한 14권 풀 기준)
      if (curationFilter === "어린이도서연구회" || curationFilter === "research-council") {
        const { getResearchCouncilBooks } = await import("@/lib/home-api");
        const books = await getResearchCouncilBooks(14, undefined, !!user);
        return filterByAgeIfSet(books, 7);
      }
      // 4. 겨울방학 / 여름방학 (홈 화면과 동일한 14권 풀 기준)
      if (curationFilter === "겨울방학" || curationFilter === "winter-vacation") {
        const { getWinterBooks } = await import("@/lib/home-api");
        const books = await getWinterBooks(14, undefined, !!user);
        return filterByAgeIfSet(books, 7);
      }
      if (curationFilter === "여름방학" || curationFilter === "summer-vacation" || curationFilter === "여름방학2026") {
        const { getSummerBooks } = await import("@/lib/home-api");
        const books = await getSummerBooks(14, undefined, !!user);
        return filterByAgeIfSet(books, 7);
      }
      // 5. AI 순수 주제 큐레이션
      if (curationFilter) {
        if (tagFilter) {
          // 도서 상세에서 학년 타겟팅(예: 초등2학년)으로 넘어온 경우
          const { getBooksByTopicTag } = await import("@/lib/home-api");
          return getBooksByTopicTag(curationFilter, 8, { age: ageFilter, gradeTag: tagFilter }, undefined, !!user);
        }
        // 홈 화면(14권 풀 + 선호 연령 우선 정렬)과 1:1 시각적 연속성 유지
        const { getBooksByTag } = await import("@/lib/home-api");
        const books = await getBooksByTag(curationFilter, 14, undefined, !!user);
        return filterByAgeIfSet(books, 7);
      }
      // 6. 연령별 추천도서 (인기순 vs 홈 화면 주간 로테이션 분기)
      if (ageFilter) {
        if (sortFilter === 'popular' || sortFilter === 'national_loan_count' || sortFilter === 'national_loan_count_desc') {
          const { getPopularBooksByAge } = await import("@/lib/home-api");
          return getPopularBooksByAge(ageFilter, 8, undefined, !!user);
        }
        const { getBooksByAge } = await import("@/lib/home-api");
        return getBooksByAge(ageFilter, 7, undefined, !!user);
      }
      return [];
    },
    enabled: shouldFetchRecommended && isMounted,
    staleTime: 5 * 60 * 1000, // 5분 캐시
    gcTime: 10 * 60 * 1000,   // 10분 캐시 유지
  });

  // 추천 도서가 준비된 경우 목록 최상단에 우선 병합 고정
  const displayBooks = useMemo(() => {
    if (!shouldFetchRecommended || recommendedBooks.length === 0) return books;

    const recIds = new Set(recommendedBooks.map(b => b.id));
    const filteredMainBooks = books.filter(b => !recIds.has(b.id));

    return [...recommendedBooks, ...filteredMainBooks];
  }, [books, recommendedBooks, shouldFetchRecommended]);

  // 추천 도서(상단 7권)가 필요한 경우 추천 도서 쿼리까지 동기화하여 첫 로드 순서 덜컹거림 및 플리커링 원천 차단
  const isListLoading = !isMounted || (isSearchWaitingState
    ? isSearchWaitingRecommendedLoading
    : (loading || (shouldFetchRecommended && isRecommendedLoading)));

  // 큐레이션 + 연령 필터 결과가 소수(1~6권)일 때 하단에 같은 테마의 다른 연령대 책 섹션 노출
  const isSparseCurationAge = isMounted &&
    !isListLoading &&
    !isSearchWaitingState &&
    !!curationFilter &&
    !!ageFilter &&
    !searchQuery &&
    !hasNextPage &&
    displayBooks.length > 0 &&
    displayBooks.length <= 6;

  // 폴백 추천 도서 활성화 조건 (0건이거나 큐레이션+연령 필터 결과가 6권 이하일 때)
  const isFallbackEnabled = isMounted && !isListLoading && !isSearchWaitingState && (displayBooks.length === 0 || isSparseCurationAge);


  // 폴백 추천 도서 fetch 쿼리
  // 큐레이션 진입 중 연령 필터 등으로 0건 또는 소수 건인 경우, 해당 큐레이션의 다른 연령대 도서를 우선 노출
  const { data: fallbackBooks = [] } = useQuery<Book[]>({
    queryKey: ['fallback-books', curationFilter, ageFilter, searchQuery, !!user],
    queryFn: async () => {
      if (curationFilter) {
        let curationFallback: Book[] = [];
        if (curationFilter === '교과서수록' || curationFilter === 'textbook') {
          const { getTextbookBooks } = await import("@/lib/home-api");
          curationFallback = await getTextbookBooks(undefined, 14, undefined, !!user);
        } else if (curationFilter === "caldecott") {
          const { getCaldecottBooks } = await import("@/lib/caldecott-api");
          const books = await getCaldecottBooks(undefined, !!user);
          curationFallback = books.slice(0, 14);
        } else if (curationFilter === "어린이도서연구회" || curationFilter === "research-council") {
          const { getResearchCouncilBooks } = await import("@/lib/home-api");
          curationFallback = await getResearchCouncilBooks(14, undefined, !!user);
        } else if (curationFilter === "겨울방학" || curationFilter === "winter-vacation") {
          const { getWinterBooks } = await import("@/lib/home-api");
          curationFallback = await getWinterBooks(14, undefined, !!user);
        } else if (curationFilter === "여름방학" || curationFilter === "summer-vacation" || curationFilter === "여름방학2026") {
          const { getSummerBooks } = await import("@/lib/home-api");
          curationFallback = await getSummerBooks(14, undefined, !!user);
        } else {
          const { getBooksByTag } = await import("@/lib/home-api");
          curationFallback = await getBooksByTag(curationFilter, 14, undefined, !!user);
        }
        if (curationFallback.length > 0) {
          return curationFallback;
        }
      }

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

  // 상단에 이미 노출된 도서는 제외한 다른 연령대 폴백 도서 (최대 8권)
  const displayFallbackBooks = useMemo(() => {
    if (displayBooks.length === 0) return fallbackBooks.slice(0, 8);
    const shownIds = new Set(displayBooks.map(b => b.id));
    return fallbackBooks.filter(b => !shownIds.has(b.id)).slice(0, 8);
  }, [fallbackBooks, displayBooks]);

  // Batch fetch loan statuses for all visible books (including fallback books)
  const visibleBooksForLoan = useMemo(() => {
    if (displayBooks.length > 0) {
      return isSparseCurationAge && displayFallbackBooks.length > 0
        ? [...displayBooks, ...displayFallbackBooks]
        : displayBooks;
    }
    return isSearchWaitingState
      ? searchWaitingRecommendedBooks
      : displayFallbackBooks;
  }, [displayBooks, isSparseCurationAge, displayFallbackBooks, isSearchWaitingState, searchWaitingRecommendedBooks]);
  const bookIds = visibleBooksForLoan.map(b => b.id).join(',');

  const { data: loanStatuses } = useQuery({
    queryKey: ['batch-loan-status', bookIds, selectedLibrary, selectedLibraryCode],
    queryFn: async () => {
      if (visibleBooksForLoan.length === 0 || !selectedLibrary) return {};
      try {
        const { fetchLoanStatuses } = await import("@/lib/api");
        return await fetchLoanStatuses(
          visibleBooksForLoan.map(b => b.id),
          selectedLibrary,
          { libCode: selectedLibraryCode }
        );
      } catch (err) {
        console.warn('Batch loan status fetch failed:', err);
        throw err;
      }
    },
    enabled: !!selectedLibrary && visibleBooksForLoan.length > 0,
    staleTime: 5 * 60 * 1000,
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

  // Track no results — 실제 값이 있는 파라미터만 전송 (undefined → GA4 "(not set)" 방지)
  useEffect(() => {
    if (!isListLoading && books.length === 0 && (searchQuery || ageFilter || curationFilter)) {
      const trimmed = searchQuery?.trim();
      // 한글 조합 중 초성 단독 입력 상태에서는 search_no_results 중복 발생 방지
      if (trimmed && /^[ㄱ-ㅎㅏ-ㅣ]+$/.test(trimmed)) return;

      const params: Record<string, string> = {};
      if (trimmed) {
        params.keyword = trimmed;
        params.search_term = trimmed;
      }
      if (ageFilter) params.age = ageFilter;
      if (curationFilter) params.curation = curationFilter;
      sendGAEvent('search_no_results', params);
    }
  }, [isListLoading, books.length, searchQuery, ageFilter, curationFilter]);

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

  const libraryControl = (
    <div className="min-w-0 max-w-full flex items-center">
      <LibrarySelector
        autoOpen={shouldAutoOpenLibrary}
        onClose={() => setShouldAutoOpenLibrary(false)}
        customTrigger={(open) =>
          selectedLibrary ? (
            <button
              type="button"
              onClick={() => {
                sendGAEvent("click_library_cta", { source: "book_list_change", authenticated: Boolean(user) });
                open();
              }}
              aria-label={`선택된 도서관: ${selectedLibrary}. 클릭하여 변경`}
              className="inline-flex items-center gap-1.5 max-w-full h-9 px-3 rounded-full bg-white border border-gray-200/90 text-[13.5px] font-semibold text-gray-800 active:bg-gray-50 active:scale-[0.98] transition-all cursor-pointer outline-none focus:outline-none"
            >
              <MapPin className="w-3.5 h-3.5 text-brand-primary shrink-0" />
              <span className="truncate">{selectedLibrary}</span>
              <ChevronDown className="w-3.5 h-3.5 text-gray-400 shrink-0" />
            </button>
          ) : (
            <button
              type="button"
              onClick={() => {
                sendGAEvent("click_library_cta", { source: "book_list", authenticated: Boolean(user) });
                open();
              }}
              aria-label="내 도서관 설정"
              className="inline-flex items-center gap-1.5 max-w-full h-9 px-3 rounded-full bg-white border border-brand-primary/60 text-[13.5px] font-semibold text-gray-800 active:bg-amber-50/70 active:scale-[0.98] transition-all cursor-pointer outline-none focus:outline-none"
            >
              <MapPin className="w-3.5 h-3.5 text-brand-primary shrink-0" />
              <span className="truncate">내 도서관 설정</span>
              <ChevronDown className="w-3.5 h-3.5 text-brand-primary/70 shrink-0" />
            </button>
          )
        }
      />
    </div>
  );

  return (
    <div className="w-full px-4">
      <div className="w-full max-w-[1200px] mx-auto">
        {!isSearchWaitingState ? (
          <div className="flex items-center justify-between gap-2 pt-0.5 pb-1.5 mb-2.5">
            <div className="flex items-center gap-1.5 shrink-0">
              {filterBar}
              {toolbarRightSlot && (
                <div className="shrink-0 flex items-center">
                  {toolbarRightSlot}
                </div>
              )}
            </div>
            <div className="min-w-0 flex items-center justify-end">
              {libraryControl}
            </div>
          </div>
        ) : (
          filterBar && (
            <div className="flex items-center justify-between gap-2 pt-0.5 pb-1.5 mb-2">
              <div className="flex items-center gap-1.5 shrink-0">
                {filterBar}
                {toolbarRightSlot && (
                  <div className="shrink-0 flex items-center">
                    {toolbarRightSlot}
                  </div>
                )}
              </div>
            </div>
          )
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
                <div className="mb-6 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2.5">
                  <div>
                    <span className="text-[13px] text-gray-500 font-semibold block mb-1">
                      가장 많이 찾는 그림책
                    </span>
                    <h3 className="text-lg sm:text-xl font-bold text-gray-900 leading-tight">
                      인기 추천 도서
                    </h3>
                  </div>
                  {selectedLibrary && (
                    <div className="self-start sm:self-auto max-w-full">
                      {libraryControl}
                    </div>
                  )}
                </div>

                {/* 도서 그리드 */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
                  {searchWaitingRecommendedBooks.map((book) => (
                    <div key={book.id}>
                      <BookItem
                        book={book}
                        loanStatus={loanStatuses?.[book.id]}
                        showLibraryInfo
                        isSaved={savedBookIds.has(book.id)}
                        onToggleSave={handleToggleBookSave}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : !isListLoading && displayBooks.length === 0 ? (
          (() => {
            const ageLabel = ageFilter ? (AGE_LABELS[ageFilter] ?? ageFilter) : '';
            const isCurationAgeEmpty = !!curationFilter && !!ageFilter;
            const emptyTitle = ageFilter
              ? (searchQuery ? `${ageLabel}에 해당하는 검색 결과가 없어요` : `${ageLabel}에 해당하는 책이 없어요`)
              : '검색 결과가 없습니다';
            const emptySubtitle = ageFilter
              ? (searchQuery ? '다른 검색어나 연령 필터로 시도해 보세요' : '')
              : '다른 검색어나 필터로 시도해 보세요';

            return (
              <div className="space-y-3 w-full">
                {/* Empty State - 폴백 도서가 있으면 슬림 인라인 알림 바, 없으면 중앙 빈 화면 */}
                {displayFallbackBooks.length > 0 ? (
                  <div className="flex items-center gap-2.5 px-5 py-3.5 rounded-2xl bg-white shadow-[0_1px_4px_rgba(0,0,0,0.06)]">
                    <Info className="w-4 h-4 text-gray-400 shrink-0" />
                    <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5 text-left">
                      <span className="text-[14px] font-semibold text-gray-700 break-keep">{emptyTitle}</span>
                      {emptySubtitle && (
                        <span className="text-[13px] text-gray-500 break-keep">{emptySubtitle}</span>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="py-16 px-4 text-center flex flex-col items-center justify-center">
                    <p className="text-[15px] font-semibold text-gray-600 break-keep">{emptyTitle}</p>
                    {emptySubtitle && (
                      <p className="mt-1 text-[13px] text-gray-400 break-keep">{emptySubtitle}</p>
                    )}
                  </div>
                )}

                {/* Fallback Recommendation Box - Level 1 shadow, no borders */}
                {displayFallbackBooks.length > 0 && (
                  <div className="p-6 bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)]">
                    {/* 2단 타이틀 구조 (서브 타이틀 위, 메인 타이틀 아래) */}
                    <div className="mb-6">
                      <span className="text-[13px] text-gray-500 font-semibold block mb-1">
                        {isCurationAgeEmpty ? '다른 연령대의 책은 어떨까요?' : '조건에 맞는 책이 없지만 이 책은 어떨까요?'}
                      </span>
                      <h3 className="text-lg sm:text-xl font-bold text-gray-900 leading-tight break-keep">
                        {isCurationAgeEmpty
                          ? (curationTitle || '이 테마의 전체 도서')
                          : ageFilter
                            ? `${ageLabel} 추천 도서`
                            : '인기 도서 추천'}
                      </h3>
                    </div>

                    {/* 도서 그리드 */}
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
                      {displayFallbackBooks.map((book) => (
                        <div key={book.id}>
                          <BookItem
                            book={book}
                            loanStatus={loanStatuses?.[book.id]}
                            showLibraryInfo
                            isSaved={savedBookIds.has(book.id)}
                            onToggleSave={handleToggleBookSave}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })()
        ) : (
          <>
            {/* Book grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
              {displayBooks.map((book) => (
                <div key={book.id}>
                  <BookItem
                    book={book}
                    loanStatus={loanStatuses?.[book.id]}
                    showLibraryInfo
                    isSaved={savedBookIds.has(book.id)}
                    onToggleSave={handleToggleBookSave}
                  />
                </div>
              ))}
            </div>

            {/* 큐레이션 + 연령 필터 결과가 소수(1~6권)일 때 같은 테마의 다른 연령대 책 섹션 추가 노출 */}
            {isSparseCurationAge && displayFallbackBooks.length > 0 && (
              <div className="mt-8 p-6 bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)]">
                <div className="mb-6">
                  <span className="text-[13px] text-gray-500 font-semibold block mb-1">
                    다른 연령대의 책은 어떨까요?
                  </span>
                  <h3 className="text-lg sm:text-xl font-bold text-gray-900 leading-tight break-keep">
                    {curationTitle || '이 테마의 전체 도서'}
                  </h3>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
                  {displayFallbackBooks.map((book) => (
                    <div key={book.id}>
                      <BookItem
                        book={book}
                        loanStatus={loanStatuses?.[book.id]}
                        showLibraryInfo
                        isSaved={savedBookIds.has(book.id)}
                        onToggleSave={handleToggleBookSave}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Infinite scroll sentinel (mobile only) */}
            {isMobile && displayBooks.length > 0 && !error && !isSparseCurationAge && (
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
          onClose={() => {
            setIsLoginModalOpen(false);
            if (typeof window !== "undefined") {
              sessionStorage.removeItem("pendingAction");
              sessionStorage.removeItem("returnUrl");
            }
          }}
        />
      </div>
    </div>
  );
}
