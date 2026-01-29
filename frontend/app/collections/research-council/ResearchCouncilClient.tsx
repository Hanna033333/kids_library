'use client'
import { useEffect, useState } from 'react'
import BookList from '@/components/BookList'
import SearchBar from '@/components/SearchBar'
import FilterBar from '@/components/FilterBar'
import IntegratedFilterModal from '@/components/IntegratedFilterModal'

export default function ResearchCouncilClient() {
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedAge, setSelectedAge] = useState<string>('전체')
    const [selectedCategory, setSelectedCategory] = useState<string>('전체')
    const [sortBy, setSortBy] = useState<'pangyo_callno' | 'title'>('pangyo_callno')
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false)

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
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            <div className="container mx-auto px-4 py-8 max-w-7xl">
                <div className="mb-8 text-center">
                    <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">📖 어린이 도서 연구회 추천</h1>
                    <p className="text-gray-600 text-lg">전문가가 엄선한 믿고 보는 필독서</p>
                </div>
                <div className="mb-6">
                    <SearchBar onSearch={setSearchQuery} onFilterClick={() => setIsFilterModalOpen(true)} />
                </div>
                <FilterBar selectedAge={selectedAge} selectedCategory={selectedCategory}
                    onAgeChange={setSelectedAge} onCategoryClick={() => setIsFilterModalOpen(true)} />
                <IntegratedFilterModal isOpen={isFilterModalOpen} onClose={() => setIsFilterModalOpen(false)}
                    mode="integrated" selectedAge={selectedAge} selectedCategory={selectedCategory}
                    selectedSort={sortBy} onAgeChange={setSelectedAge} onCategoryChange={setSelectedCategory}
                    onSortChange={(sort: string) => setSortBy(sort as 'pangyo_callno' | 'title')} />
                <BookList searchQuery={searchQuery} ageFilter={selectedAge}
                    categoryFilter={selectedCategory} curationFilter="어린이도서연구회" sortFilter={sortBy} />
            </div>
        </div>
    )
}
