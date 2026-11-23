"use client";

import { useState, useEffect, useRef, useMemo, useCallback, type ReactNode } from "react";
import { useQuery, useQueryClient, keepPreviousData } from "@tanstack/react-query";
import BookItem from "./BookItem";
import { useBooks } from "@/hooks/useBooks";
import { Book, BooksResponse } from "@/lib/types";
import { Spinner } from "@/components/ui/Spinner";
import { PageLoader } from "@/components/ui/PageLoader";
import { useLibrary } from "@/context/LibraryContext";
import LibrarySelector from "@/components/LibrarySelector";
import { sendGAEvent } from "@/lib/analytics";
import { useAuth } from "@/context/AuthContext";
import LoginPromptModal from "@/components/ui/LoginPromptModal";
import { useRouter } from "next/navigation";
import { MapPin, ChevronRight } from "lucide-react";
import { supabase } from "@/lib/supabase";
import { saveBook, unsaveBook, getSavedBookIds } from "@/lib/supabase-api";

const ITEMS_PER_PAGE = 24;

interface BookListProps {
  searchQuery?: string;
  ageFilter?: string;
  curationFilter?: string;
  tagFilter?: string;
  sortFilter?: string;
  initialPage?: BooksResponse;
  filterBar?: ReactNode;
}

export default function BookList({
  searchQuery,
  ageFilter,
  curationFilter,
  tagFilter,
  sortFilter = "title",
  initialPage,
  filterBar,
}: BookListProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [loginModalConfig, setLoginModalConfig] = useState({
    title: "도서관 헛걸음 끝! 대출 가능한 책만 1초 스캔",
    description: "우리 동네 도서관만 등록하면,\n지금 빌릴 수 있는 책과 책장 위치가 바로 보여요.",
  });
  const [shouldAutoOpenLibrary, setShouldAutoOpenLibrary] = useState(false);
  const [savedBookIds, setSavedBookIds] = useState<Set<number>>(new Set());
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
            // 신규 가입 모달이 동시에 뜨는 경우에는 온보딩 모달 안에서 도서관을 선택하므로 중복 바텀시트 오픈 방지
            if (!isNewSignupModalOpening) {
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
      setLoginModalConfig({
        title: "도서관 갈 때 까먹지 않게 내 책장에 쏙!",
        description: "마음에 드는 책을 장바구니에 담아두면 도서관에서 청구기호와 대출 가능 여부를 1초 만에 꺼내볼 수 있어요.",
      });
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
      if (visibleBooksForLoan.length === 0 || !selectedLibrary) return {};
      try {
        const { fetchLoanStatuses } = await import("@/lib/api");
        return await fetchLoanStatuses(visibleBooksForLoan.map(b => b.id), selectedLibrary);
      } catch (err) {
        console.warn('Batch loan status fetch failed:', err);
        throw err;
      }
    },
    enabled: !!selectedLibrary && visibleBooksForLoan.length > 0,
    staleTime: 3 * 60 * 1000, // 3 minutes cache
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

  const libraryControl = !user ? (
    <button
      type="button"
      onClick={() => {
        if (typeof window !== "undefined") {
          sessionStorage.setItem("returnUrl", window.location.pathname + window.location.search);
          sessionStorage.setItem("pendingAction", "open_library_selector");
        }
        sendGAEvent("click_library_cta_unauth", { source: "book_list" });
        setLoginModalConfig({
          title: "도서관 헛걸음 끝! 대출 가능한 책만 1초 스캔",
          description: "우리 동네 도서관만 등록하면,\n지금 빌릴 수 있는 책과 책장 위치가 바로 보여요.",
        });
        setIsLoginModalOpen(true);
      }}
      className="inline-flex items-center gap-1.5 px-3 sm:px-3.5 py-2 rounded-full bg-white border border-amber-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] text-[13px] font-bold text-gray-900 active:bg-amber-50 active:scale-95 transition-all cursor-pointer outline-none focus:outline-none shrink-0"
    >
      <MapPin className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-amber-500 shrink-0" />
      <span className="sm:hidden">대출 조회</span>
      <span className="hidden sm:inline">우리 동네 도서관 대출 확인</span>
      <ChevronRight className="w-3.5 h-3.5 text-gray-400 shrink-0" />
    </button>
  ) : !selectedLibrary ? (
    <LibrarySelector
      autoOpen={shouldAutoOpenLibrary}
      customTrigger={(open) => (
        <button
          type="button"
          onClick={open}
          className="inline-flex items-center gap-1.5 px-3 sm:px-3.5 py-2 rounded-full bg-white border border-amber-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] text-[13px] font-bold text-gray-900 active:bg-amber-50 active:scale-95 transition-all cursor-pointer outline-none focus:outline-none shrink-0"
        >
          <MapPin className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-amber-500 shrink-0" />
          <span className="sm:hidden">도서관 선택</span>
          <span className="hidden sm:inline">내 도서관 설정하기</span>
          <ChevronRight className="w-3.5 h-3.5 text-gray-400 shrink-0" />
        </button>
      )}
    />
  ) : (
    <div className="max-w-[135px] sm:max-w-none flex items-center">
      <LibrarySelector autoOpen={shouldAutoOpenLibrary} />
    </div>
  );

  return (
    <div className="w-full px-4">
      <div className="w-full max-w-[1200px] mx-auto">
        {!isSearchWaitingState && filterBar ? (
          <div className="flex items-center justify-between gap-2 pt-0.5 pb-1.5 mb-2">
            <div className="min-w-0 flex-1">
              {filterBar}
            </div>
            <div className="shrink-0 flex items-center pl-1">
              {libraryControl}
            </div>
          </div>
        ) : (
          <>
            {!isSearchWaitingState && (
              <div className="flex items-center justify-end mt-0 mb-2.5 px-1">
                {libraryControl}
              </div>
            )}
            {filterBar && (
              <div className="pt-0.5 pb-1.5 mb-2">
                {filterBar}
              </div>
            )}
          </>
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
                    {ageFilter ? `${({ '0-3': '0~3세', '4-7': '4~7세', '8-12': '8~12세', '13+': '13세 이상' } as Record<string, string>)[ageFilter] ?? ageFilter} 추천 도서` : "인기 도서 추천"}
                  </h3>
                </div>

                {/* 도서 그리드 */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-6">
                  {fallbackBooks.map((book) => (
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
          title={loginModalConfig.title}
          description={loginModalConfig.description}
        />
      </div>
    </div>
  );
}
