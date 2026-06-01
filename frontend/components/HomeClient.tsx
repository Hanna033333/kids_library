"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import BookList from "@/components/BookList";
import { BooksResponse } from "@/lib/types";
import { useAuth } from "@/context/AuthContext";
import { LogIn, User, Search, Share2 } from "lucide-react";
import Link from "next/link";
import IntegratedFilterModal from "@/components/IntegratedFilterModal";
import PageHeader from "@/components/PageHeader";
import { sendGAEvent } from "@/lib/analytics";
import UserAvatar from "@/components/UserAvatar";
import Toast from "@/components/ui/Toast";

interface HomeClientProps {
    overrideCuration?: string;
    overrideAge?: string;
}

export default function HomeClient({ overrideCuration, overrideAge }: HomeClientProps) {
    const router = useRouter();
    const searchParams = useSearchParams();

    // URL에서 초기 상태 읽기 (teen → 13+ 정규화)
    const normalizeAge = (age: string) => age === "teen" ? "13+" : age;
    const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || "");
    const [ageFilter, setAgeFilter] = useState(normalizeAge(overrideAge || searchParams.get('age') || ""));
    const [categoryFilter, setCategoryFilter] = useState(searchParams.get('category') || "전체");
    const [curationFilter, setCurationFilter] = useState(overrideCuration || searchParams.get('curation') || "");
    
    // AI 큐레이션은 기본적으로 신뢰도(confidence_score) 높은 순으로 정렬하여 홈 화면과 동일한 순서를 유지
    const [sortFilter, setSortFilter] = useState(() => {
        const urlSort = searchParams.get('sort');
        if (urlSort) return urlSort;
        
        const curation = searchParams.get('curation');
        if (curation && !['겨울방학', 'winter-vacation', '어린이도서연구회', 'research-council', 'caldecott'].includes(curation)) {
            return 'confidence_score_desc'; // confidence_score_desc 라는 가상의 sort key 사용
        }
        return 'pangyo_callno';
    });
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
    const [filterModalMode, setFilterModalMode] = useState<"integrated" | "category">("integrated");
    const [isSearchVisible, setIsSearchVisible] = useState(false);
    const { user, signOut } = useAuth();
    const [toastMessage, setToastMessage] = useState("");

    // AI 큐레이션 태그 여부 (알려진 non-AI 큐레이션 제외)
    const NON_AI_CURATIONS = ['겨울방학', 'winter-vacation', '어린이도서연구회', 'research-council', 'caldecott'];
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
        const age = normalizeAge(overrideAge || searchParams.get('age') || "");
        const category = searchParams.get('category') || "전체";
        const curation = overrideCuration || searchParams.get('curation') || "";
        const sort = searchParams.get('sort') || (curation && !['겨울방학', 'winter-vacation', '어린이도서연구회', 'research-council', 'caldecott'].includes(curation) ? 'confidence_score_desc' : 'pangyo_callno');

        setSearchQuery(q);
        setAgeFilter(age);
        setCategoryFilter(category);
        setCurationFilter(curation);
        setSortFilter(sort);
    }, [searchParams, overrideAge, overrideCuration]);

    const handleSearch = useCallback((query: string) => {
        setSearchQuery(query);
        sendGAEvent('search', { keyword: query });
        updateURL({ q: query, age: ageFilter, category: categoryFilter, sort: sortFilter });
    }, [ageFilter, categoryFilter, sortFilter, updateURL]);

    const handleAgeChange = useCallback((age: string) => {
        setAgeFilter(age);
        sendGAEvent('filter_change', { type: 'age', value: age });
        updateURL({ q: searchQuery, age, category: categoryFilter, sort: sortFilter });
    }, [searchQuery, categoryFilter, sortFilter, updateURL]);

    const handleCategoryChange = useCallback((category: string) => {
        setCategoryFilter(category);
        sendGAEvent('filter_change', { type: 'category', value: category });
        updateURL({ q: searchQuery, age: ageFilter, category, sort: sortFilter });
    }, [searchQuery, ageFilter, sortFilter, updateURL]);

    const handleSortChange = useCallback((sort: string) => {
        setSortFilter(sort);
        sendGAEvent('filter_change', { type: 'sort', value: sort });
        updateURL({ q: searchQuery, age: ageFilter, category: categoryFilter, sort });
    }, [searchQuery, ageFilter, categoryFilter, updateURL]);

    const openIntegratedFilter = () => {
        setFilterModalMode("integrated");
        setIsFilterModalOpen(true);
    };

    const openCategoryFilter = () => {
        setFilterModalMode("category");
        setIsFilterModalOpen(true);
    };

    // URL 파라미터에 따라 동적 타이틀 결정
    const getPageTitle = () => {
        if (curationFilter === 'research-council' || curationFilter === '어린이도서연구회') return '어린이도서연구회 추천';
        if (curationFilter === 'winter-vacation' || curationFilter === '겨울방학') return '겨울방학 추천도서';
        if (curationFilter === 'caldecott') return '칼데콧 수상작';
        
        // AI 큐레이션 타이틀 매핑
        const aiCurationTitles: Record<string, string> = {
            '잠자리': '포근한 잠자리 책',
            '감정조절': '마음 처방전',
            '자존감': '자존감 그림책',
            '사회성': '사회성 기르기',
            '인체': '신비한 우리 몸',
            '판타지': '판타지 세계',
            '환경보호': '환경 학교',
            '생명존중': '동물 친구들',
            '가족사랑': '가족 이야기',
            '배려': '나눔과 배려',
            '모험': '두근두근 모험',
            '전래동화': '재밌는 옛이야기',
            '예술감성': '꼬마 예술가',
            '자연관찰': '신비한 자연 관찰',
            '역사이야기': '지혜로운 역사',
            '과학원리': '꼬마 과학자',
            '다양성': '세계 시민 학교',
            '적응': '즐거운 유치원',
            '우리문화': '전통과 유산',
            '계절': '여름의 추억'
        };

        if (curationFilter) return aiCurationTitles[curationFilter] || curationFilter;

        if (ageFilter === '0-3') return '0~3세 추천 도서';
        if (ageFilter === '4-7') return '4~7세 추천 도서';
        if (ageFilter === '8-12') return '8~12세 추천 도서';
        if (ageFilter === 'teen' || ageFilter === '13+') return '13세 이상 추천 도서';
        if (searchQuery) return '도서 검색';
        return '도서 검색';
    }

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
                backHref="/"
                rightSlot={
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setIsSearchVisible(!isSearchVisible)}
                            className="text-gray-500 hover:text-gray-900 transition-colors p-1"
                            aria-label="검색 열기"
                        >
                            <Search className="w-5 h-5" />
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

            {/* 필터 바 (간소화 및 공유 액션 연동) */}
            <FilterBar
                selectedAge={ageFilter}
                onAgeChange={handleAgeChange}
                selectedCategory={categoryFilter}
                onFilterClick={openIntegratedFilter}
                showFilterButton={!isAiCuration}
                onShareClick={handleShareCuration}
                showShareButton={!!curationFilter || (!!ageFilter && !searchQuery)}
            />

            {/* 통합 필터 모달 */}
            <IntegratedFilterModal
                isOpen={isFilterModalOpen}
                onClose={() => setIsFilterModalOpen(false)}
                mode={filterModalMode}
                searchQuery={searchQuery}
                selectedCategory={categoryFilter}
                onCategoryChange={handleCategoryChange}
                selectedAge={ageFilter}
                onAgeChange={handleAgeChange}
                selectedSort={sortFilter}
                onSortChange={handleSortChange}
            />

            {/* 책 리스트 */}
            <div className="w-full max-w-7xl mx-auto pb-4 md:pb-6 pt-0">
                <BookList
                    searchQuery={searchQuery || undefined}
                    ageFilter={ageFilter || undefined}
                    categoryFilter={categoryFilter === "전체" ? undefined : categoryFilter}
                    curationFilter={curationFilter || undefined}
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
