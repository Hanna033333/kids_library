'use client'
import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import BookList from '@/components/BookList'
import SearchBar from '@/components/SearchBar'
import FilterBar from '@/components/FilterBar'
import IntegratedFilterModal from '@/components/IntegratedFilterModal'
import PageHeader from '@/components/PageHeader'
import { sendGAEvent } from '@/lib/analytics'

import { BooksResponse } from '@/lib/types'

interface AgeCollectionClientProps {
    age: string;
    initialPage?: BooksResponse;
}

const ageDisplayNames: Record<string, string> = {
    '0-3': '0~3세', '4-7': '4~7세', '8-12': '8~12세', '13+': '13세 이상', 'teen': '13세 이상'
}
const ageDescriptions: Record<string, string> = {
    '0-3': '영유아 발달에 꼭 맞는 그림책을 만나보세요',
    '4-7': '상상력과 언어 발달을 돕는 유아 그림책',
    '8-12': '독서 습관을 기르는 초등학생 필독서',
    'teen': '사고력을 키우는 청소년 권장도서'
}

export default function AgeCollectionClient({ age, initialPage }: AgeCollectionClientProps) {
    const router = useRouter()
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedAge, setSelectedAge] = useState<string>(age === 'teen' ? '13+' : age)
    const [sortBy, setSortBy] = useState<'callno' | 'title'>('title')
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false)

    const handleSearch = useCallback((query: string) => {
        setSearchQuery(query)
        const trimmed = query.trim()
        if (trimmed && !/^[ㄱ-ㅎㅏ-ㅣ]+$/.test(trimmed)) {
            sendGAEvent('search', {
                search_term: trimmed,
                keyword: trimmed,
                age: selectedAge,
                page_path: `/collections/age/${age}?q=${encodeURIComponent(trimmed)}`,
            })
        }
    }, [selectedAge, age])

    // 탭 클릭 시 URL 이동 → 뒤로가기 UX 정상화 + GA 추적 정확도 향상
    const handleAgeChange = (newAge: string) => {
        setSelectedAge(newAge)
        sendGAEvent('filter_change', { type: 'age', value: newAge || 'all' })
        const urlAge = newAge === '13+' ? 'teen' : newAge
        if (urlAge !== age) {
            router.push(`/collections/age/${urlAge}`)
        }
    }

    // 서버가 조회한 연령·검색·정렬 조건이 같을 때만 첫 페이지를 재사용한다.
    const currentInitialPage = selectedAge === (age === 'teen' ? '13+' : age) && !searchQuery && sortBy === 'title' ? initialPage : undefined;

    return (
        <div className="min-h-screen bg-[#F7F7F7]">
            <PageHeader title={`${ageDisplayNames[age]} 추천 도서`} showHome={true} />
            <div className="container mx-auto px-4 py-8 max-w-7xl">
                <div className="mb-4">
                    <SearchBar onSearch={handleSearch} />
                </div>
                <IntegratedFilterModal isOpen={isFilterModalOpen} onClose={() => setIsFilterModalOpen(false)}
                    selectedAge={selectedAge} selectedSort={sortBy} onAgeChange={setSelectedAge}
                    onSortChange={(sort: string) => setSortBy(sort as 'callno' | 'title')} />
                <BookList
                    searchQuery={searchQuery}
                    ageFilter={selectedAge}
                    sortFilter={sortBy}
                    initialPage={currentInitialPage}
                    filterBar={
                        <FilterBar
                            embedded={true}
                            selectedAge={selectedAge}
                            onAgeChange={handleAgeChange}
                            onFilterClick={() => setIsFilterModalOpen(true)}
                        />
                    }
                />
            </div>
        </div>
    )
}
