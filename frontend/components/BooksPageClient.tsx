"use client";

import { useState, useCallback, useEffect, useMemo, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import SearchBar from "@/components/SearchBar";
import BookList from "@/components/BookList";
import { BooksResponse } from "@/lib/types";
import { useAuth } from "@/context/AuthContext";
import { LogIn, User, Search, Share2, Home, ChevronRight } from "lucide-react";
import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import { sendGAEvent } from "@/lib/analytics";
import UserAvatar from "@/components/UserAvatar";
import Toast from "@/components/ui/Toast";
import FilterBar from "@/components/FilterBar";
import IntegratedFilterModal from "@/components/IntegratedFilterModal";
import BackButton from "@/components/BackButton";
import { ALL_TAXONOMY } from "@/lib/constants/taxonomy";
import { cleanCurationTag } from "@/lib/utils/curation-filter";
import { getAgeGroupKey } from "@/lib/utils/age";
import { PageLoader } from "@/components/ui/PageLoader";

interface BooksPageClientProps {
    overrideCuration?: string;
    overrideAge?: string;
    initialPage?: BooksResponse;
    initialSort?: string;
    initialAvailableAges?: string[];
}

const FILTERABLE_AGE_GROUPS = ['0-3', '4-7', '8-12'] as const;

// AI 큐레이션이 아닌 정적/특수 큐레이션 목록 (AI 신뢰도순 정렬 제외)
const NON_AI_CURATIONS = ['겨울방학', 'winter-vacation', '여름방학', 'summer-vacation', '여름방학2026', '어린이도서연구회', 'research-council', 'caldecott', 'textbook', '교과서수록'];

export default function BooksPageClient({ overrideCuration, overrideAge, initialPage, initialSort, initialAvailableAges }: BooksPageClientProps) {
    const initialBooks = initialPage?.data;
    const router = useRouter();
    const searchParams = useSearchParams();

    // URL에서 초기 상태 읽기 (teen → 13+ 정규화, 학년 태그 정규화)
    const normalizeAge = (age: string) => age === "teen" ? "13+" : age;
    const normalizeGradeTag = (tag: string) => {
        if (!tag || tag === 'all') return '';
        const match = tag.match(/초등\s*(\d)학년|초등학교\s*(\d)학년|(\d)학년/);
        if (match) {
            const num = match[1] || match[2] || match[3];
            return `초등${num}학년`;
        }
        return tag;
    };

    // curation 파라미터 오염 방어 헬퍼 (?age=8-12 등이 curation 값에 붙어 들어온 경우 자동 분리 복구)
    const parseCurationParams = (rawCuration: string | null) => {
        if (!rawCuration) return { cleanTag: '', extraAge: '', extraTag: '', extraSort: '' };
        if (rawCuration.includes('?') || rawCuration.includes('&')) {
            try {
                const parts = rawCuration.split(/[?&]/);
                const pureTag = parts[0];
                const queryString = rawCuration.substring(pureTag.length + 1);
                const urlParams = new URLSearchParams(queryString);
                return {
                    cleanTag: cleanCurationTag(pureTag),
                    extraAge: urlParams.get('age') || '',
                    extraTag: urlParams.get('tag') || '',
                    extraSort: urlParams.get('sort') || '',
                };
            } catch {
                return { cleanTag: cleanCurationTag(rawCuration), extraAge: '', extraTag: '', extraSort: '' };
            }
        }
        return { cleanTag: cleanCurationTag(rawCuration), extraAge: '', extraTag: '', extraSort: '' };
    };

    const rawRouteCuration = overrideCuration || searchParams.get('curation') || "";
    const parsedRouteCuration = parseCurationParams(rawRouteCuration);
    const routeSearchQuery = searchParams.get('q') || "";
    const routeAuthorFilter = searchParams.get('author') ? decodeURIComponent(searchParams.get('author')!) : "";
    const routeAgeFilter = normalizeAge(overrideAge || searchParams.get('age') || parsedRouteCuration.extraAge || "");
    const routeCurationFilter = parsedRouteCuration.cleanTag;
    const rawRouteTag = searchParams.get('tag') ? decodeURIComponent(searchParams.get('tag')!) : parsedRouteCuration.extraTag;
    const routeTagFilter = normalizeGradeTag(rawRouteTag);
    const routeSortFilter = searchParams.get('sort') || parsedRouteCuration.extraSort || (routeCurationFilter && !NON_AI_CURATIONS.includes(routeCurationFilter) ? 'confidence_score_desc' : 'title');

    const [searchQuery, setSearchQuery] = useState(routeSearchQuery);
    const [authorFilter, setAuthorFilter] = useState(routeAuthorFilter);
    const [ageFilter, setAgeFilter] = useState(routeAgeFilter);
    const [curationFilter, setCurationFilter] = useState(routeCurationFilter);
    const [tagFilter, setTagFilter] = useState(routeTagFilter);
    const [isSearchVisible, setIsSearchVisible] = useState(() => {
        return !!searchQuery || (!overrideCuration && !searchParams.get('curation') && !searchParams.get('age') && !searchParams.get('author'));
    });

    // AI 큐레이션은 기본적으로 신뢰도(confidence_score) 높은 순으로 정렬하여 홈 화면과 동일한 순서를 유지
    const [sortFilter, setSortFilter] = useState(() => {
        return routeSortFilter;
    });
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
    const { user, isLoading: authLoading, preferredChildAge, signOut } = useAuth();
    const [toastMessage, setToastMessage] = useState("");

    // 교과서 수록도서 큐레이션 여부
    const isTextbook = curationFilter === 'textbook' || curationFilter === '교과서수록';

    // AI 큐레이션 태그 여부 (알려진 non-AI 큐레이션 제외)
    const isAiCuration = !!curationFilter && !NON_AI_CURATIONS.includes(curationFilter);

    // 특정 큐레이션 진입 시 해당 큐레이션 내 연령대별 도서 존재 여부 조회 (0권인 연령 칩 비활성화용)
    const initialCurationMatches = curationFilter === (overrideCuration || parsedRouteCuration.cleanTag);
    const derivedInitialAges = useMemo(() => {
        if (!initialCurationMatches) return undefined;
        if (initialAvailableAges) return initialAvailableAges;
        if (initialBooks && initialBooks.length > 0 && initialBooks.length < 24) {
            return Array.from(new Set(initialBooks.map(b => b.age ? getAgeGroupKey(b.age) : '').filter(Boolean)));
        }
        return undefined;
    }, [initialCurationMatches, initialAvailableAges, initialBooks]);

    const { data: availableAgesForCuration } = useQuery<string[]>({
        queryKey: ['curation-available-ages', curationFilter],
        queryFn: async () => {
            const { getAvailableAgesForCuration } = await import('@/lib/home-api');
            return getAvailableAgesForCuration(curationFilter);
        },
        enabled: !!curationFilter && !isTextbook,
        initialData: derivedInitialAges,
        staleTime: 10 * 60 * 1000,
    });

    const disabledAges = useMemo(() => {
        if (!curationFilter || isTextbook || !availableAgesForCuration) return [];
        return FILTERABLE_AGE_GROUPS.filter(age => !availableAgesForCuration.includes(age));
    }, [curationFilter, isTextbook, availableAgesForCuration]);

    // URL 업데이트 함수
    const updateURL = useCallback((params: Record<string, string>) => {
        // Use window.location.search to get current params without dependency
        const newParams = new URLSearchParams(window.location.search);

        Object.entries(params).forEach(([key, value]) => {
            if (value && value !== "전체") {
                newParams.set(key, value);
            } else {
                newParams.delete(key);
            }
        });

        router.replace(`?${newParams.toString()}`, { scroll: false });
    }, [router]);

    // URL 파라미터 변경 시 상태 동기화 (브라우저 뒤로가기/앞으로가기 대응)
    useEffect(() => {
        setSearchQuery(routeSearchQuery);
        setAuthorFilter(routeAuthorFilter);
        setAgeFilter(routeAgeFilter);
        setCurationFilter(routeCurationFilter);
        setTagFilter(routeTagFilter);
        setSortFilter(routeSortFilter);

        if (routeAuthorFilter || routeCurationFilter || routeAgeFilter) {
            setIsSearchVisible(false);
        } else if (routeSearchQuery || (!routeCurationFilter && !routeAgeFilter && !routeTagFilter && !routeAuthorFilter)) {
            setIsSearchVisible(true);
        }
    }, [routeSearchQuery, routeAuthorFilter, routeAgeFilter, routeCurationFilter, routeTagFilter, routeSortFilter]);

    // 도서 리스트 진입 시, 로그인 유저의 선호 연령대가 설정되어 있고 URL에 age가 없으면 해당 연령대 필터를 기본값으로 자동 선택
    const initialAgeAppliedRef = useRef(false);
    useEffect(() => {
        if (authLoading || initialAgeAppliedRef.current) return;
        initialAgeAppliedRef.current = true;

        if (user && preferredChildAge && !routeAgeFilter && !overrideAge && !searchParams.get('age') && !isTextbook) {
            setAgeFilter(preferredChildAge);
            updateURL({ age: preferredChildAge });
        }
    }, [authLoading, user, preferredChildAge, routeAgeFilter, overrideAge, searchParams, isTextbook, updateURL]);

    const POPULAR_THEME_CHIPS = [
        { label: '잠자리', tag: '잠자리' },
        { label: '자존감', tag: '자존감' },
        { label: '첫 사회성', tag: '사회성' },
        { label: '기관적응', tag: '적응' },
        { label: '감정·마음', tag: '감정조절' },
        { label: '공룡', tag: '공룡' },
        { label: '자연·생태', tag: '자연관찰' },
        { label: '예술·창의', tag: '예술감성' },
        { label: '호기심·과학', tag: '과학원리' },
        { label: '가족사랑', tag: '가족사랑' },
    ];

    // 이모티콘 제거 헬퍼 함수
    const stripEmoji = (text: string): string =>
        text.replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]|[\u2600-\u27BF\uFE0F\u200D]/g, '').trim();

    const handleCurationSelect = useCallback((tag: string) => {
        const nextCuration = curationFilter === tag ? "" : tag;
        setCurationFilter(nextCuration);
        setTagFilter("");
        sendGAEvent('filter_change', { type: 'curation_chip', value: nextCuration || 'all' });
        updateURL({ q: searchQuery, age: ageFilter, curation: nextCuration, sort: sortFilter, tag: "", author: authorFilter });
    }, [curationFilter, searchQuery, ageFilter, sortFilter, authorFilter, updateURL]);

    const lastTrackedSearchRef = useRef<string>("");

    // URL 직접 진입(/books?q=...) 또는 SearchDiscoveryHub 키워드 클릭 진입 시에도 search 이벤트 누락 방지
    useEffect(() => {
        const trimmed = routeSearchQuery.trim();
        if (!trimmed || /^[ㄱ-ㅎㅏ-ㅣ]+$/.test(trimmed)) return;
        if (lastTrackedSearchRef.current === trimmed) return;
        lastTrackedSearchRef.current = trimmed;
        sendGAEvent('search', {
            search_term: trimmed,
            keyword: trimmed,
            page_path: typeof window !== 'undefined' ? `${window.location.pathname}?q=${encodeURIComponent(trimmed)}` : `/books?q=${encodeURIComponent(trimmed)}`
        });
    }, [routeSearchQuery]);

    const handleSearch = useCallback((query: string) => {
        if (query === searchQuery) return;
        setSearchQuery(query);
        setAuthorFilter("");
        const trimmed = query.trim();
        if (trimmed && !/^[ㄱ-ㅎㅏ-ㅣ]+$/.test(trimmed)) {
            lastTrackedSearchRef.current = trimmed;
            sendGAEvent('search', {
                search_term: trimmed,
                keyword: trimmed,
                page_path: typeof window !== 'undefined' ? `${window.location.pathname}?q=${encodeURIComponent(trimmed)}` : `/books?q=${encodeURIComponent(trimmed)}`
            });
        }
        updateURL({ q: query, age: ageFilter, curation: curationFilter, sort: sortFilter, tag: tagFilter, author: "" });
    }, [searchQuery, ageFilter, curationFilter, sortFilter, tagFilter, updateURL]);

    const handleAgeChange = useCallback((age: string) => {
        setAgeFilter(age);
        sendGAEvent('filter_change', { type: 'age', value: age });
        updateURL({ q: searchQuery, age, curation: curationFilter, sort: sortFilter, tag: tagFilter, author: authorFilter });
    }, [searchQuery, curationFilter, sortFilter, tagFilter, authorFilter, updateURL]);

    const handleTagChange = useCallback((tag: string) => {
        setTagFilter(tag);
        sendGAEvent('filter_change', { type: 'textbook_grade', value: tag || 'all' });
        updateURL({ q: searchQuery, age: ageFilter, curation: curationFilter, sort: sortFilter, tag, author: authorFilter });
    }, [searchQuery, ageFilter, curationFilter, sortFilter, authorFilter, updateURL]);

    const handleSortChange = useCallback((sort: string) => {
        setSortFilter(sort);
        sendGAEvent('filter_change', { type: 'sort', value: sort });
        updateURL({ q: searchQuery, age: ageFilter, curation: curationFilter, sort, tag: tagFilter, author: authorFilter });
    }, [searchQuery, ageFilter, curationFilter, tagFilter, authorFilter, updateURL]);

    const openIntegratedFilter = () => {
        setIsFilterModalOpen(true);
    };


    // URL 파라미터에 따라 동적 타이틀 결정 (공백 포함 11자 이내, 이모티콘 없이 순수 텍스트로 노출)
    const getPageTitle = () => {
        const currentTag = tagFilter || (searchParams.get('tag') ? decodeURIComponent(searchParams.get('tag')!) : "");

        // 0. 작가별 전용 리스트 타이틀
        if (authorFilter) {
            return authorFilter.length > 7 ? authorFilter : `${authorFilter} 작가의 책`;
        }

        // 1. 교과서 수록도서
        if (curationFilter === 'textbook' || curationFilter === '교과서수록') {
            return '교과서 수록도서';
        }

        // 2. 특수 큐레이션
        if (curationFilter === 'research-council' || curationFilter === '어린이도서연구회') return '어린이도서연구회 추천';
        if (curationFilter === 'winter-vacation' || curationFilter === '겨울방학' || curationFilter === '겨울방학2026') return '겨울방학 추천도서';
        if (curationFilter === 'summer-vacation' || curationFilter === '여름방학' || curationFilter === '여름방학2026') return '여름방학 추천도서';
        if (curationFilter === 'caldecott') return '칼데콧 수상작';

        // 3. ALL_TAXONOMY 기반 매핑 (이모티콘 제거)
        if (curationFilter) {
            const matched = ALL_TAXONOMY.find(item => item.tag === curationFilter || item.slug === curationFilter);
            if (matched) {
                return stripEmoji(matched.title);
            }
            return stripEmoji(curationFilter);
        }

        // 4. 연령별 및 검색 타이틀
        if (ageFilter === '0-3') return '0~3세 추천 도서';
        if (ageFilter === '4-7') return '4~7세 추천 도서';
        if (ageFilter === '8-12') return '8~12세 추천 도서';
        if (ageFilter === 'teen' || ageFilter === '13+') return '13세 이상 추천 도서';
        if (searchQuery) return '도서 검색';
        return '도서 검색';
    };

    // 큐레이션 컨텍스트 한 줄 설명 (스레드/외부 랜딩 시 테마 맥락 즉시 전달)
    const curationSubtitle = useMemo(() => {
        if (!curationFilter) return "";
        if (curationFilter === 'textbook' || curationFilter === '교과서수록') {
            return '초등학교 국어 교과서에 실린 학년별 필독 도서';
        }
        if (curationFilter === 'research-council' || curationFilter === '어린이도서연구회') {
            return '어린이도서연구회가 엄선한 전문가 추천 필독서';
        }
        if (curationFilter === 'caldecott') {
            return '2000~2026 칼데콧 메달 수상 세계 최고 그림책';
        }
        if (curationFilter === 'winter-vacation' || curationFilter === '겨울방학' || curationFilter === '겨울방학2026') {
            return '사서가 엄선한 실패 없는 겨울방학 추천 도서';
        }
        if (curationFilter === 'summer-vacation' || curationFilter === '여름방학' || curationFilter === '여름방학2026') {
            return '교육청과 사서가 엄선한 여름방학 추천 도서';
        }
        const matched = ALL_TAXONOMY.find(item => item.tag === curationFilter || item.slug === curationFilter);
        return matched ? stripEmoji(matched.subtitle) : "";
    }, [curationFilter]);

    const handleShareCuration = async () => {
        const curationTitle = getPageTitle();
        let shareUrl = '';
        let shareText = '';

        if (curationFilter) {
            const isSlugPath = window.location.pathname.startsWith('/collections/curation/');
            const baseQuery = isSlugPath ? '' : `curation=${encodeURIComponent(curationFilter)}&`;
            shareUrl = `${window.location.origin}${window.location.pathname}?${baseQuery}utm_source=share&utm_medium=social&utm_campaign=curation_${encodeURIComponent(curationFilter)}`;
            shareText = `우리 아이에게 딱 맞는 [${curationTitle}] 도서 리스트예요. 내 주변 도서관 대출 가능 여부까지 바로 확인해 보세요!`;
        } else if (ageFilter) {
            const isAgePath = window.location.pathname.startsWith('/collections/age/');
            const baseQuery = isAgePath ? '' : `age=${encodeURIComponent(ageFilter)}&`;
            shareUrl = `${window.location.origin}${window.location.pathname}?${baseQuery}utm_source=share&utm_medium=social&utm_campaign=age_${encodeURIComponent(ageFilter)}`;
            shareText = `우리 아이 나이에 딱 맞는 [${curationTitle}] 리스트예요. 내 주변 도서관 대출 가능 여부까지 바로 확인해 보세요!`;
        } else {
            return;
        }

        const shareData = {
            title: `책자리 - ${curationTitle}`,
            text: shareText,
            url: shareUrl
        }

        try {
            if (typeof navigator.share === 'function') {
                await navigator.share(shareData)
            } else {
                await navigator.clipboard.writeText(shareUrl)
                setToastMessage('추천 리스트 링크가 복사되었습니다! 단톡방에 공유해 보세요.')
            }
            sendGAEvent('share_curation_list', {
                curation_tag: curationFilter || undefined,
                age_tag: ageFilter || undefined,
                curation_title: curationTitle,
                method: typeof navigator.share === 'function' ? 'native_share' : 'clipboard'
            })
        } catch (err) {
            console.error('Share failed:', err)
        }
    }

    // 서버 첫 페이지는 큐레이션·정렬이 같고 추가 필터가 없을 때만 전달한다.
    const isRouteStateSynced =
        searchQuery === routeSearchQuery &&
        authorFilter === routeAuthorFilter &&
        ageFilter === routeAgeFilter &&
        curationFilter === routeCurationFilter &&
        tagFilter === routeTagFilter &&
        sortFilter === routeSortFilter;

    // 같은 클라이언트 컴포넌트에서 URL만 바뀌는 순간, 이전 큐레이션 캐시가 한 프레임 노출되는 것을 차단한다.
    if (!isRouteStateSynced) {
        return <PageLoader />;
    }

    const currentInitialPage = (initialPage && sortFilter === initialSort && curationFilter === overrideCuration && !searchQuery && !authorFilter && !ageFilter && !tagFilter)
        ? initialPage
        : undefined;

    return (
        <main className="min-h-screen">
            {/* Header */}
            <PageHeader
                title={getPageTitle()}
                showHome={true}
                rightSlot={
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setIsSearchVisible(!isSearchVisible)}
                            className="text-gray-500 hover:text-gray-900 transition-colors p-1"
                            aria-label="검색 열기"
                        >
                            <Search className="w-6 h-6" />
                        </button>
                        {user ? (
                            <button
                                onClick={() => router.push('/my-page')}
                                className="hover:text-gray-900 transition-colors p-1 flex items-center justify-center group"
                                aria-label="마이 페이지"
                            >
                                <UserAvatar user={user} size={24} className="text-gray-500 group-hover:text-gray-900 transition-colors" />
                            </button>
                        ) : (
                            <button
                                onClick={() => router.push('/auth/signup')}
                                className="hover:text-gray-900 transition-colors p-1 flex items-center justify-center group"
                                aria-label="로그인"
                            >
                                <UserAvatar user={null} size={24} className="text-gray-500 group-hover:text-gray-900 transition-colors" />
                            </button>
                        )}
                    </div>
                }
            />


            {/* 검색 바 */}
            <div className={`transition-all ${isSearchVisible ? 'block' : 'hidden'}`}>
                <SearchBar
                    onSearch={handleSearch}
                    initialQuery={searchQuery}
                />
            </div>

            {/* 큐레이션 컨텍스트 바 (스레드 등 외부 랜딩 시 테마 맥락 전달 + 공유 버튼) */}
            {curationSubtitle && !isSearchVisible && (
                <div className="w-full px-4 pt-2 pb-0.5">
                    <div className="w-full max-w-[1200px] mx-auto flex items-center justify-between gap-2">
                        <p className="text-[13px] font-medium text-gray-600 leading-snug line-clamp-1">
                            {curationSubtitle}
                        </p>
                        <button
                            type="button"
                            onClick={handleShareCuration}
                            className="shrink-0 inline-flex items-center gap-1 px-2.5 py-1.5 rounded-full bg-white border border-gray-200/80 text-[12px] font-semibold text-gray-700 active:bg-gray-100 active:scale-95 transition-all outline-none focus:outline-none"
                            aria-label="큐레이션 리스트 공유하기"
                        >
                            <Share2 className="w-3.5 h-3.5 text-gray-500" />
                            <span>공유</span>
                        </button>
                    </div>
                </div>
            )}

            {/* 필터 바 (교과서 수록도서: 초등 1~6학년 필터 / 일반: 연령대 필터) */}
            <FilterBar
                selectedAge={ageFilter}
                onAgeChange={handleAgeChange}
                onFilterClick={openIntegratedFilter}
                showFilterButton={!!searchQuery || !!authorFilter}
                isTextbook={isTextbook}
                selectedTag={tagFilter}
                onTagChange={handleTagChange}
                disabledAges={disabledAges}
            />

            {/* 통합 필터 모달 */}
            <IntegratedFilterModal
                isOpen={isFilterModalOpen}
                onClose={() => setIsFilterModalOpen(false)}
                selectedAge={ageFilter}
                onAgeChange={handleAgeChange}
                selectedSort={sortFilter}
                onSortChange={handleSortChange}
                isTextbook={isTextbook}
                selectedTag={tagFilter}
                onTagChange={handleTagChange}
                disabledAges={disabledAges}
            />

            {/* 책 리스트 */}
            <div className="w-full max-w-7xl mx-auto pb-4 md:pb-6 pt-0.5">
                <BookList
                    searchQuery={searchQuery || authorFilter || undefined}
                    ageFilter={ageFilter || undefined}
                    curationFilter={curationFilter || undefined}
                    tagFilter={tagFilter || undefined}
                    sortFilter={sortFilter}
                    initialPage={currentInitialPage}
                />
            </div>

            {/* 토스트 팝업 알림 */}
            <Toast
                message={toastMessage}
                isVisible={!!toastMessage}
                onClose={() => setToastMessage('')}
            />
        </main>
    );
}
