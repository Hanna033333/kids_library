'use client'
import { useEffect, useState } from 'react'
import BookList from '@/components/BookList'
import SearchBar from '@/components/SearchBar'
import FilterBar from '@/components/FilterBar'
import IntegratedFilterModal from '@/components/IntegratedFilterModal'

interface AgeCollectionClientProps { age: string }

const ageDisplayNames: Record<string, string> = {
    '0-3': '0-3세', '4-7': '4-7세', '8-12': '8-12세', 'teen': '13세 이상'
}
const ageDescriptions: Record<string, string> = {
    '0-3': '영유아 발달에 꼭 맞는 그림책을 만나보세요',
    '4-7': '상상력과 언어 발달을 돕는 유아 그림책',
    '8-12': '독서 습관을 기르는 초등학생 필독서',
    'teen': '사고력을 키우는 청소년 권장도서'
}

export default function AgeCollectionClient({ age }: AgeCollectionClientProps) {
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedAge, setSelectedAge] = useState<string>(age)
    const [selectedCategory, setSelectedCategory] = useState<string>('전체')
    const [sortBy, setSortBy] = useState<'pangyo_callno' | 'title'>('pangyo_callno')
    const [isFilterModalOpen, setIsFilterModalOpen] = useState(false)

    useEffect(() => {
        const jsonLd = {
            '@context': 'https://schema.org',
            '@type': 'ItemList',
            name: `${ageDisplayNames[age]} 추천 도서`,
            description: ageDescriptions[age]
        }
        const script = document.createElement('script')
        script.type = 'application/ld+json'
        script.text = JSON.stringify(jsonLd)
        document.head.appendChild(script)
        return () => { document.head.removeChild(script) }
    }, [age])

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            <div className="container mx-auto px-4 py-8 max-w-7xl">
                <div className="mb-8 text-center">
                    <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
                        📚 {ageDisplayNames[age]} 추천 도서
                    </h1>
                    <p className="text-gray-600 text-lg">{ageDescriptions[age]}</p>
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
                    categoryFilter={selectedCategory} sortFilter={sortBy} />
            </div>
        </div>
    )
}
