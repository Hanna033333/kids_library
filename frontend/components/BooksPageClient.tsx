"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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

interface BooksPageClientProps {
    overrideCuration?: string;
    overrideAge?: string;
}

// AI 큐레이션이 아닌 정적/특수 큐레이션 목록 (AI 신뢰도순 정렬 제외)
const NON_AI_CURATIONS = ['겨울방학', 'winter-vacation', '여름방학', 'summer-vacation', '여름방학2026', '어린이도서연구회', 'research-council', 'caldecott', 'textbook', '교과서수록'];

export default function BooksPageClient({ overrideCuration, overrideAge }: BooksPageClientProps) {
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

    const initialRawCuration = overrideCuration || searchParams.get('curation') || "";
    const parsedInitialCuration = parseCurationParams(initialRawCuration);

    const rawInitialTag = searchParams.get('tag') ? decodeURIComponent(searchParams.get('tag')!) : parsedInitialCuration.extraTag;
    const initialTag = normalizeGradeTag(rawInitialTag);
    const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || "");
    const [authorFilter, setAuthorFilter] = useState(searchParams.get('author') || "");
    const [ageFilter, setAgeFilter] = useState(normalizeAge(overrideAge || searchParams.get('age') || parsedInitialCuration.extraAge || ""));
    const [curationFilter, setCurationFilter] = useState(parsedInitialCuration.cleanTag);
    const [tagFilter, setTagFilter] = useState(initialTag);
    const [isSearchVisible, setIsSearchVisible] = useState(() => {
        return !!searchQuery || (!overrideCuration && !searchParams.get('curation') && !searchParams.get('age') && !searchParams.get('author'));
    });
    
    // AI 큐레이션은 기본적으로 신뢰도(confidence_score) 높은 순으로 정렬하여 홈 화면과 동일한 순서를 유지
    const [sortFilter, setSortFilter] = useState(() => {
        const urlSort = searchParams.get('sort') || parsedInitialCuration.extraSort;
        if (urlSort) return urlSort;
        
        const curation = parsedInitialCuration.cleanTag;
        if (curation && !NON_AI_CURATIONS.includes(curation)) {
            return 'confidence_score_desc';
        }
        return 'pangyo_callno';
    });
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
    const { user, signOut } = useAuth();
    const [toastMessage, setToastMessage] = useState("");

    // 교과서 수록도서 큐레이션 여부
    const isTextbook = curationFilter === 'textbook' || curationFilter === '교과서수록';

    // AI 큐레이션 태그 여부 (알려진 non-AI 큐레이션 제외)
    const isAiCuration = !!curationFilter && !NON_AI_CURATIONS.includes(curationFilter);

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
        const q = searchParams.get('q') || "";
        const author = searchParams.get('author') ? decodeURIComponent(searchParams.get('author')!) : "";
        const rawCuration = overrideCuration || searchParams.get('curation') || "";
        const parsed = parseCurationParams(rawCuration);

        const age = normalizeAge(overrideAge || searchParams.get('age') || parsed.extraAge || "");
        const curation = parsed.cleanTag;
        const rawTag = searchParams.get('tag') ? decodeURIComponent(searchParams.get('tag')!) : parsed.extraTag;
        const tag = normalizeGradeTag(rawTag);
        const sort = searchParams.get('sort') || parsed.extraSort || (curation && !NON_AI_CURATIONS.includes(curation) ? 'confidence_score_desc' : 'pangyo_callno');

        setSearchQuery(q);
        setAuthorFilter(author);
        setAgeFilter(age);
        setCurationFilter(curation);
        setTagFilter(tag);
        setSortFilter(sort);

        if (author || curation || age) {
            setIsSearchVisible(false);
        } else if (q || (!curation && !age && !tag && !author)) {
            setIsSearchVisible(true);
        }
    }, [searchParams, overrideAge, overrideCuration]);

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

    const handleSearch = useCallback((query: string) => {
        setSearchQuery(query);
        setAuthorFilter("");
        sendGAEvent('search', { search_term: query, keyword: query });
        updateURL({ q: query, age: ageFilter, curation: curationFilter, sort: sortFilter, tag: tagFilter, author: "" });
    }, [ageFilter, curationFilter, sortFilter, tagFilter, updateURL]);

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

    const handleShareCuration = async () => {
        const curationTitle = getPageTitle();
        let shareUrl = '';
        let shareText = '';
        
        if (curationFilter) {
            shareUrl = `${window.location.origin}${window.location.pathname}?curation=${encodeURIComponent(curationFilter)}&utm_source=share&utm_medium=social&utm_campaign=curation_${encodeURIComponent(curationFilter)}`;
            shareText = `우리 아이에게 딱 맞는 사서 추천 [${curationTitle}] 도서 리스트예요. 로그인 없이 대출 가능 여부까지 즉시 확인해 보세요!`;
        } else if (ageFilter) {
            // 연령별 상세 큐레이션 공유 대응
            shareUrl = `${window.location.origin}${window.location.pathname}?age=${encodeURIComponent(ageFilter)}&utm_source=share&utm_medium=social&utm_campaign=age_${encodeURIComponent(ageFilter)}`;
            shareText = `우리 아이 나이에 딱 맞는 [${curationTitle}] 리스트예요. 로그인 없이 대출 가능 여부까지 즉시 확인해 보세요!`;
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

            {/* 필터 바 (교과서 수록도서: 초등 1~6학년 필터 / 일반: 연령대 필터) */}
            <FilterBar
                selectedAge={ageFilter}
                onAgeChange={handleAgeChange}
                onFilterClick={openIntegratedFilter}
                showFilterButton={!!searchQuery || !!authorFilter}
                isTextbook={isTextbook}
                selectedTag={tagFilter}
                onTagChange={handleTagChange}
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
            />

            {/* 책 리스트 */}
            <div className="w-full max-w-7xl mx-auto pb-4 md:pb-6 pt-2">
                <BookList
                    searchQuery={searchQuery || authorFilter || undefined}
                    ageFilter={ageFilter || undefined}
                    curationFilter={curationFilter || undefined}
                    tagFilter={tagFilter || undefined}
                    sortFilter={sortFilter}
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
