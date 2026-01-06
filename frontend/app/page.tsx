'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Search } from 'lucide-react'
import { getBooksByAge, getResearchCouncilBooks, type Book } from '@/lib/home-api'

export default function HomePage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedAge, setSelectedAge] = useState('4-7')
  const [ageBooks, setAgeBooks] = useState<Book[]>([])
  const [researchBooks, setResearchBooks] = useState<Book[]>([])
  const [loading, setLoading] = useState(true)

  // 연령별 책 로드
  useEffect(() => {
    setLoading(true)
    getBooksByAge(selectedAge, 5).then(books => {
      setAgeBooks(books)
      setLoading(false)
    })
  }, [selectedAge])

  // 도서 연구회 책 로드
  useEffect(() => {
    getResearchCouncilBooks(5).then(setResearchBooks)
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/books?q=${encodeURIComponent(searchQuery)}`)
    } else {
      router.push('/books')
    }
  }

  return (
    <main className="min-h-screen bg-[#F7F7F7]">
      {/* Hero Section - 검색창 */}
      <section className="bg-white py-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          {/* 로고 */}
          <div className="mb-8">
            <img
              src="/logo.png"
              alt="책방구"
              className="h-16 w-auto mx-auto"
            />
          </div>

          {/* 검색창 */}
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="아이 연령 / 책 제목으로 검색"
                className="w-full px-6 py-4 pl-14 text-lg bg-white text-gray-900 placeholder:text-gray-400 border-2 border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent shadow-lg"
              />
              <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400 w-6 h-6" />
            </div>
          </form>
        </div>
      </section>

      {/* 연령별 추천 섹션 */}
      <section className="py-12 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">우리 아이 나이에 딱!</h2>

          {/* 연령 탭 */}
          <div className="flex gap-3 mb-8">
            {[
              { key: '0-3', label: '0-3세' },
              { key: '4-7', label: '4-7세' },
              { key: '8-12', label: '8-12세' },
              { key: '13+', label: '13세+' }
            ].map(age => (
              <button
                key={age.key}
                onClick={() => setSelectedAge(age.key)}
                className={`px-6 py-2 rounded-lg font-medium transition-all ${selectedAge === age.key
                    ? 'bg-[#F59E0B] text-white shadow-md'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
              >
                {age.label}
              </button>
            ))}
          </div>

          {/* 책 그리드 */}
          {loading ? (
            <div className="text-center py-12 text-gray-500">로딩 중...</div>
          ) : ageBooks.length > 0 ? (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-6">
                {ageBooks.map(book => (
                  <BookCard key={book.id} book={book} />
                ))}
              </div>
              <div className="text-right">
                <Link
                  href={`/books?age=${selectedAge}`}
                  className="inline-flex items-center text-[#F59E0B] font-medium hover:underline"
                >
                  더보기 →
                </Link>
              </div>
            </>
          ) : (
            <div className="text-center py-12 text-gray-500">
              해당 연령대의 책이 없습니다
            </div>
          )}
        </div>
      </section>

      {/* 도서 연구회 추천 섹션 */}
      <section className="py-12 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">어린이 도서 연구회 추천</h2>

          {researchBooks.length > 0 ? (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-6">
                {researchBooks.map(book => (
                  <BookCard key={book.id} book={book} />
                ))}
              </div>
              <div className="text-right">
                <Link
                  href="/books?curation=어린이도서연구회"
                  className="inline-flex items-center text-[#F59E0B] font-medium hover:underline"
                >
                  더보기 →
                </Link>
              </div>
            </>
          ) : (
            <div className="text-center py-12 text-gray-500">
              추천 도서가 없습니다
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <p className="mb-2">책방구 | 어린이 도서관 책 검색</p>
          <p className="text-sm">© 2026 책방구. All rights reserved.</p>
        </div>
      </footer>
    </main>
  )
}

// 책 카드 컴포넌트
function BookCard({ book }: { book: Book }) {
  return (
    <Link href={`/book/${book.id}`} className="group">
      <div className="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
        {/* 책 표지 */}
        <div className="aspect-[3/4] bg-gray-100 relative overflow-hidden">
          {book.image_url ? (
            <img
              src={book.image_url}
              alt={book.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-300">
              <span className="text-4xl">📚</span>
            </div>
          )}
        </div>

        {/* 책 정보 */}
        <div className="p-3">
          <h3 className="font-bold text-sm text-gray-900 line-clamp-2 mb-1">
            {book.title}
          </h3>
          <p className="text-xs text-gray-500 mb-2">{book.author}</p>
          {book.category && (
            <span className="inline-block px-2 py-0.5 bg-blue-50 text-blue-600 text-xs rounded">
              {book.category}
            </span>
          )}
          {book.pangyo_callno && (
            <p className="text-xs text-gray-400 mt-1">{book.pangyo_callno}</p>
          )}
        </div>
      </div>
    </Link>
  )
}
