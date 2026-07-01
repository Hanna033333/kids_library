"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import SearchBar from "@/components/SearchBar";
import BookList from "@/components/BookList";
import { BooksResponse } from "@/lib/types";
import { useAuth } from "@/context/AuthContext";
import { LogIn, User, Search, Share2, Home } from "lucide-react";
import Link from "next/link";
import PageHeader from "@/components/PageHeader";
import { sendGAEvent } from "@/lib/analytics";
import UserAvatar from "@/components/UserAvatar";
import Toast from "@/components/ui/Toast";
import FilterBar from "@/components/FilterBar";
import IntegratedFilterModal from "@/components/IntegratedFilterModal";
import BackButton from "@/components/BackButton";

interface BooksPageClientProps {
    overrideCuration?: string;
    overrideAge?: string;
}

export default function BooksPageClient({ overrideCuration, overrideAge }: BooksPageClientProps) {
    const router = useRouter();
    const searchParams = useSearchParams();

    // URL에서 초기 상태 읽기 (teen → 13+ 정규화)
    const normalizeAge = (age: string) => age === "teen" ? "13+" : age;
    const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || "");
    const [ageFilter, setAgeFilter] = useState(normalizeAge(overrideAge || searchParams.get('age') || ""));
    const [categoryFilter, setCategoryFilter] = useState(searchParams.get('category') || "전체");
    const [curationFilter, setCurationFilter] = useState(overrideCuration || searchParams.get('curation') || "");
    const [isSearchVisible, setIsSearchVisible] = useState(() => {
        return !!searchQuery || (!overrideCuration && !searchParams.get('curation') && !searchParams.get('age'));
    });
    
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

        if (q || (!curation && !age)) {
            setIsSearchVisible(true);
        }
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
            '잠자리': '스르륵 꿀잠 그림책',
            '감정조절': '마음 처방전 그림책',
            '자존감': '단단한 자존감 그림책',
            '사회성': '다정한 첫 사회성',
            '인체': '신비한 우리 몸 그림책',
            '판타지': '호기심 가득 판타지',
            '환경보호': '초록 생태 환경',
            '생명존중': '사랑스러운 동물들',
            '가족사랑': '따뜻한 가족 사랑',
            '배려': '다정한 배려 그림책',
            '모험': '씩씩한 모험 이야기',
            '전래동화': '구수한 옛이야기',
            '예술감성': '감성 풍부 꼬마 예술가',
            '자연관찰': '호기심 자연 관찰',
            '역사이야기': '지혜로운 역사',
            '과학원리': '호기심 가득 과학 원리',
            '다양성': '열린 마음 다양성 학교',
            '적응': '유치원과 학교생활',
            '우리문화': '지혜 가득 문화 유산',
            '계절': '아름다운 사계절',
            '상실': '이별을 다독이는 책',
            '용기': '씩씩한 용기 그림책',
            '우정': '다정한 내 친구',
            '정직': '바른 마음 정직',
            '나눔': '기쁨 두 배 나눔',
            '분노조절': '화를 가라앉히는 책',
            '슬픔': '슬픔을 다독이는 책',
            '질투': '시샘을 지우는 책',
            '두려움': '밤이 무섭지 않은 책',
            '끈기': '포기하지 않는 끈기',
            '위로': '따뜻한 위로 그림책',
            '행복': '매일 매일 행복',
            '용서': '미안해와 괜찮아',
            '규칙': '약속을 지키는 그림책',
            '다문화': '세계 시민 그림책',
            '진로': '내 꿈을 찾는 그림책',
            '경제': '현명한 돈 쓰기',
            '의사소통': '대화가 즐거운 책',
            '평화': '평화를 지키는 그림책',
            '장애': '편견 없는 눈그림책',
            '양성평등': '모두를 위한 평등',
            '이웃': '우리 동네 이웃 사촌',
            '미디어': '스마트폰 조절',
            '곤충': '꿈틀꿈틀 곤충 나라',
            '우주': '별빛 가득 우주 여행',
            '공룡': '거대한 공룡의 세계',
            '바다': '푸른 바다 탐험',
            '식물': '무럭무럭 초록 식물',
            '날씨': '변화무쌍 날씨 탐구',
            '코딩': '생각하는 컴퓨터 코딩',
            '인공지능': '로봇과 인공지능',
            '수학': '재미있는 수학 놀이',
            '발명': '위대한 발명 이야기',
            '음악': '아름다운 소리와 음악',
            '연극': '배우들의 무대 연극',
            '세계역사': '세계 역사와 문화',
            '명화': '미술관에서 만난 명화',
            '건축': '튼튼한 건축과 집',
            '명절': '한국의 정겨운 명절',
            '전통놀이': '민속 전통 놀이',
            '한글': '소중한 우리 한글',
            '글쓰기': '상상 가득 글쓰기',
            '유머': '웃음 빵빵 유머 그림책',
            '추리': '명탐정의 추리 비밀',
            '상상력': '상상의 날개를 활짝',
            '하늘': '하늘을 나는 상상',
            '요리': '맛있는 요리조리',
            '패션': '내 멋진 옷과 패션',
            '탈것': '씽씽 달리는 탈것',
            '스포츠': '튼튼한 신체 스포츠',
            '괴물': '친근한 괴물 친구들',
            '미래도시': '꿈꾸는 미래 도시',
            '신체활동': '신나게 몸을 움직여요',
            '자연재해': '자연의 거대한 힘',
            '생활습관': '깨끗하고 올바른 습관',
            '인문지리': '세계 지도 여행',
            '동물도감': '생생한 동물 도감',
            '미래상상': '상상 속 외계인'
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

            {/* 필터 바 (간소화) */}
            <FilterBar
                selectedAge={ageFilter}
                onAgeChange={handleAgeChange}
                selectedCategory={categoryFilter}
                onFilterClick={openIntegratedFilter}
                showFilterButton={!!searchQuery}
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
            <div className="w-full max-w-7xl mx-auto pb-4 md:pb-6 pt-2">
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
