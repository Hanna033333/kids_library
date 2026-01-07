'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Search, Bookmark, LogOut, ChevronRight, Bell } from 'lucide-react'
import { getBooksByAge, getResearchCouncilBooks, type Book } from '@/lib/home-api'
import { useAuth } from '@/context/AuthContext'

export default function HomePage() {
  const router = useRouter()
  const { user, signOut } = useAuth()
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
      {/* Header - 책 리스트와 동일 */}
      <header className="w-full bg-white border-b border-gray-100 flex items-center justify-between px-6 py-4 sticky top-0 z-50">
        <div className="w-1/3"></div>
        <div className="w-1/3 flex justify-center">
          <button
            onClick={() => router.push('/')}
            className="relative inline-flex items-center cursor-pointer"
          >
            <img
              src="/logo.png"
              alt="책방구"
              className="h-10 w-auto"
            />
            <span className="absolute top-1 -right-9 text-gray-400 text-xs font-bold leading-none italic">
              beta
            </span>
          </button>
        </div>
        <div className="w-1/3 flex justify-end items-center gap-4">
          {user && (
            <div className="flex items-center gap-3">
              <Link
                href="/my-library"
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-600 flex items-center gap-1 text-sm font-medium"
                title="내 서재"
              >
                <Bookmark className="w-5 h-5" />
                <span className="hidden sm:inline">내 서재</span>
              </Link>
              <button
                onClick={() => signOut()}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-600"
                title="로그아웃"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      </header>

      {/* 검색 바 - 책 리스트와 동일 */}
      <div className="w-full sticky top-[73px] z-20 bg-[#F7F7F7]/95 backdrop-blur-sm px-4 py-4 transition-all">
        <form onSubmit={handleSearch} className="w-full max-w-[1200px] mx-auto flex gap-3">
          <div className="relative group flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="어떤 책을 찾으시나요?"
              className="w-full px-5 py-3 pl-12 pr-10 bg-white text-gray-900 placeholder:text-gray-400 border border-transparent rounded-lg shadow-[0_2px_15px_rgba(0,0,0,0.04)] focus:outline-none focus:ring-2 focus:ring-[#F59E0B]/20 focus:scale-[1.01] transition-all"
            />
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5 group-focus-within:text-[#F59E0B] transition-colors" />

            {/* Clear button */}
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"
                aria-label="검색어 지우기"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            )}
          </div>
        </form>
      </div>

      {/* 연령별 추천 섹션 */}
      <section className="py-8 px-4">
        <div className="max-w-[1200px] mx-auto">
          <div className="flex items-center justify-between mb-4 px-2">
            <h2 className="text-xl font-bold text-gray-900">우리 아이 나이에 딱!</h2>
            <Link
              href={`/books?age=${selectedAge}`}
              className="text-gray-900 hover:text-gray-600 transition-colors"
            >
              <ChevronRight className="w-6 h-6" />
            </Link>
          </div>

          {/* 연령 탭 */}
          <div className="flex gap-2 mb-6 px-2">
            {[
              { key: '0-3', label: '0-3세' },
              { key: '4-7', label: '4-7세' },
              { key: '8-12', label: '8-12세' },
              { key: '13+', label: '13세+' }
            ].map(age => (
              <button
                key={age.key}
                onClick={() => setSelectedAge(age.key)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${selectedAge === age.key
                  ? 'bg-[#F59E0B] text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
                  }`}
              >
                {age.label}
              </button>
            ))}
          </div>

          {/* 책 그리드 - 좌우 스크롤 */}
          {loading ? (
            <div className="overflow-x-auto scrollbar-hide -mx-4 px-4">
              <div className="flex gap-4 pb-2">
                {[1, 2, 3, 4, 5].map((i, index, array) => (
                  <div key={i} className={`flex-shrink-0 w-[160px] sm:w-[180px] ${index === array.length - 1 ? 'pr-4' : ''}`}>
                    <div className="flex flex-col bg-white rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-gray-100 overflow-hidden h-full animate-pulse">
                      {/* 이미지 스켈레톤 */}
                      <div className="w-full aspect-[1/1.1] bg-gray-200"></div>
                      {/* 정보 스켈레톤 */}
                      <div className="p-4 space-y-3">
                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                        <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : ageBooks.length > 0 ? (
            <>
              <div className="overflow-x-auto scrollbar-hide -mx-4 px-4">
                <div className="flex gap-4 pb-2">
                  {ageBooks.map((book, index) => (
                    <div key={book.id} className={`flex-shrink-0 w-[160px] sm:w-[180px] ${index === ageBooks.length - 1 ? 'pr-4' : ''}`}>
                      <BookCard book={book} />
                    </div>
                  ))}
                </div>
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
      <section className="py-8 px-4 bg-white">
        <div className="max-w-[1200px] mx-auto">
          <div className="flex items-center justify-between mb-6 px-2">
            <h2 className="text-xl font-bold text-gray-900">어린이 도서 연구회 추천</h2>
            <Link
              href="/books?curation=어린이도서연구회"
              className="text-gray-900 hover:text-gray-600 transition-colors"
            >
              <ChevronRight className="w-6 h-6" />
            </Link>
          </div>

          {researchBooks.length > 0 ? (
            <>
              <div className="overflow-x-auto scrollbar-hide -mx-4 px-4">
                <div className="flex gap-4 pb-2">
                  {researchBooks.map((book, index) => (
                    <div key={book.id} className={`flex-shrink-0 w-[160px] sm:w-[180px] ${index === researchBooks.length - 1 ? 'pr-4' : ''}`}>
                      <BookCard book={book} />
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12 text-gray-500">
              추천 도서가 없습니다
            </div>
          )}
        </div>
      </section>

      {/* 디바이더 */}
      <div className="border-t border-gray-200"></div>

      {/* 공지사항 섹션 */}
      <section className="py-6 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <a
            href="https://notion.so/your-notice-link"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 text-gray-700 hover:text-gray-900 transition-colors group"
          >
            <Bell className="w-5 h-5 text-[#F59E0B] group-hover:text-[#D97706] transition-colors" />
            <span className="text-sm font-medium">12/16(화) 서비스 업데이트 안내</span>
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-sm">© 2026 책방구. All rights reserved.</p>
        </div>
      </footer>
    </main>
  )
}

// 책 카드 컴포넌트 - BookItem과 동일한 UI
function BookCard({ book }: { book: Book }) {
  // Helper to normalize age strings
  function normalizeAge(rawAge: string): string {
    if (!rawAge) return ""
    const age = rawAge.replace(/\s/g, "")

    if (age.includes("8~13세")) return "8-12세"
    if (["청소년", "13세", "14세", "15세", "16세", "17세", "18세", "성인"].some(k => age.includes(k))) return "13세+"
    if (["초등", "8세", "9세", "10세", "11세", "12세"].some(k => age.includes(k))) return "8-12세"
    if (["유아", "유치", "4세", "5세", "6세", "7세"].some(k => age.includes(k))) return "4-7세"
    if (["영유아", "0세", "1세", "2세", "3세"].some(k => age.includes(k))) return "0-3세"

    return rawAge
  }

  const displayAge = normalizeAge(book.age || "")

  return (
    <Link
      href={`/book/${book.id}`}
      className="flex flex-col bg-white rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-gray-100 overflow-hidden transition-all hover:-translate-y-1 hover:shadow-md h-full group"
    >
      {/* 1. 이미지 영역 (상단) */}
      <div className="relative w-full aspect-[1/1.1] bg-[#F9FAFB] overflow-hidden flex items-center justify-center">
        {book.image_url ? (
          <img
            src={book.image_url}
            alt={book.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="flex flex-col items-center justify-center w-full h-full text-gray-300">
            <span className="text-4xl mb-2">📚</span>
            <span className="text-[10px] uppercase tracking-wider font-medium opacity-60">No Image</span>
          </div>
        )}

        {/* 태그 (이미지 위에 오버레이) */}
        <div className="absolute top-3 left-3 flex gap-1.5 flex-wrap">
          {book.category && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/90 text-gray-600 font-bold shadow-sm backdrop-blur-sm">
              {book.category}
            </span>
          )}
          {displayAge && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-black/60 text-white font-medium shadow-sm backdrop-blur-sm">
              {displayAge}
            </span>
          )}
        </div>
      </div>

      {/* 2. 정보 영역 (하단) */}
      <div className="flex-1 p-4 flex flex-col items-start bg-white">
        <h3 className="text-base font-bold text-gray-900 leading-[1.35] mb-1.5 line-clamp-2 tracking-tight group-hover:text-gray-700 transition-colors">
          {book.title}
        </h3>

        <p className="text-[15px] font-extrabold text-[#F59E0B] tracking-tight mb-3 truncate w-full">
          {book.pangyo_callno}
        </p>

        <div className="mt-auto pt-3 border-t border-gray-50 w-full flex items-center justify-between text-xs font-medium">
          <span className="text-gray-400 truncate max-w-[60%]">{book.publisher}</span>
        </div>
      </div>
    </Link>
  )
}
