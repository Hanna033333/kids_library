'use client'
import { useEffect, useState, useCallback, useRef } from 'react'
import BookList from '@/components/BookList'
import SearchBar from '@/components/SearchBar'
import FilterBar from '@/components/FilterBar'
import IntegratedFilterModal from '@/components/IntegratedFilterModal'
import PageHeader from '@/components/PageHeader'
import { useAuth } from '@/context/AuthContext'
import { sendGAEvent } from '@/lib/analytics'

export default function ResearchCouncilClient() {
    const { user, isLoading: authLoading, preferredChildAge } = useAuth()
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedAge, setSelectedAge] = useState<string>('')
    const [sortBy, setSortBy] = useState<'callno' | 'title'>('title')
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false)
    const initialAgeAppliedRef = useRef(false)

    useEffect(() => {
        if (authLoading || initialAgeAppliedRef.current) return
        initialAgeAppliedRef.current = true

        if (user && preferredChildAge) {
            setSelectedAge(preferredChildAge)
        }
    }, [authLoading, user, preferredChildAge])

    const handleSearch = useCallback((query: string) => {
        setSearchQuery(query)
        const trimmed = query.trim()
        if (trimmed && !/^[ㄱ-ㅎㅏ-ㅣ]+$/.test(trimmed)) {
            sendGAEvent('search', {
                search_term: trimmed,
                keyword: trimmed,
                curation: '어린이도서연구회',
                page_path: `/collections/research-council?q=${encodeURIComponent(trimmed)}`,
            })
        }
    }, [])

    useEffect(() => {
        const jsonLd = {
            '@context': 'https://schema.org', '@type': 'ItemList',
            name: '어린이 도서 연구회 추천 도서', description: '전문가가 엄선한 믿고 보는 어린이 필독서'
        }
        const script = document.createElement('script')
        script.type = 'application/ld+json'
        script.text = JSON.stringify(jsonLd)
        document.head.appendChild(script)
        return () => { document.head.removeChild(script) }
    }, [])

    return (
        <div className="min-h-screen bg-[#F7F7F7]">
            <PageHeader title="어린이도서연구회" showHome={true} />
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
                    curationFilter="어린이도서연구회"
                    sortFilter={sortBy}
                    filterBar={
                        <FilterBar
                            embedded={true}
                            selectedAge={selectedAge}
                            onAgeChange={setSelectedAge}
                            onFilterClick={() => setIsFilterModalOpen(true)}
                        />
                    }
                />
            </div>
        </div>
    )
}
