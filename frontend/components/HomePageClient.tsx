'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

import { Search, Bookmark, LogOut, ChevronRight, Bell, Snowflake, BookOpen, User } from 'lucide-react'
import { getBooksByAge, getResearchCouncilBooks, getWinterBooks } from '@/lib/home-api'
import { type Book, type LibraryInfo } from '@/lib/types'
import { useAuth } from '@/context/AuthContext'
import LibrarySelector from '@/components/LibrarySelector'
import { useLibrary } from '@/context/LibraryContext'
import Footer from '@/components/Footer'
import { getAgeDisplayLabel } from '@/lib/utils/age'
import ConfirmModal from '@/components/ui/ConfirmModal'
import { sendGAEvent } from '@/lib/analytics'
import Toast from '@/components/ui/Toast'
import UserAvatar from '@/components/UserAvatar'

interface HomePageClientProps {
  // initialWinterBooks?: Book[];
  initialCaldecottBooks?: Book[];
  initialResearchBooks?: Book[];
  initialAgeBooks?: Book[];
  initialSelectedAge?: string;
}

export default function HomePageClient({
  // initialWinterBooks = [],
  initialCaldecottBooks = [],
  initialResearchBooks = [],
  initialAgeBooks = [],
  initialSelectedAge = '4-7'
}: HomePageClientProps) {
  const router = useRouter()
  const { user, signOut } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedAge, setSelectedAge] = useState(() => {
    // localStorage에서 마지막 선택 연령 가져오기 (재방문자 대응)
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('lastSelectedAge')
      if (saved) return saved
    }
    return initialSelectedAge
  })

  const [ageBooks, setAgeBooks] = useState<Book[]>(initialAgeBooks)
  const [researchBooks, setResearchBooks] = useState<Book[]>(initialResearchBooks)
  // const [winterBooks, setWinterBooks] = useState<Book[]>(initialWinterBooks)
  const [caldecottBooks] = useState<Book[]>(initialCaldecottBooks)

  // 초기 데이터가 있으면 로딩 상태 false
  const [loading, setLoading] = useState(initialAgeBooks.length === 0)

  // 회원 탈퇴 팝업 상태
  const [isWithdrawnPopupOpen, setIsWithdrawnPopupOpen] = useState(false)
  const [logoutToastMessage, setLogoutToastMessage] = useState('')
  const [isSignupCompleteOpen, setIsSignupCompleteOpen] = useState(false)

  // 회원 탈퇴 후 랜딩 시 팝업 띄우기
  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (sessionStorage.getItem('showWithdrawnPopup') === 'true') {
        setIsWithdrawnPopupOpen(true)
        sessionStorage.removeItem('showWithdrawnPopup')
      }
      if (sessionStorage.getItem('showLogoutToast') === 'true') {
        setLogoutToastMessage('로그아웃 되었습니다.')
        sessionStorage.removeItem('showLogoutToast')
      }
      if (sessionStorage.getItem('showSignupComplete') === 'true') {
        setIsSignupCompleteOpen(true)
        sessionStorage.removeItem('showSignupComplete')
      }
    }
  }, [])

  // 연령별 책 로드 (초기 데이터가 있고 연령이 초기값과 같으면 스킵)
  useEffect(() => {
    // 이미 데이터가 있고, 선택된 연령이 초기 연령과 같으면 페칭 안함 (SSR 활용)
    if (ageBooks.length > 0 && selectedAge === initialSelectedAge) {
      setLoading(false)
      return
    }

    setLoading(true)
    getBooksByAge(selectedAge, 7).then(books => {
      setAgeBooks(books)
      setLoading(false)
    })
  }, [selectedAge, initialSelectedAge]) // ageBooks 의존성 제거 (무한 루프 방지)

  // 연령 선택 시 localStorage에 저장
  useEffect(() => {
    if (selectedAge && typeof window !== 'undefined') {
      localStorage.setItem('lastSelectedAge', selectedAge)
    }
  }, [selectedAge])

  // 도서 연구회 책 로드 (초기 데이터 없으면 로드)
  useEffect(() => {
    if (researchBooks.length === 0) {
      getResearchCouncilBooks(7).then(setResearchBooks)
    }
  }, []) // researchBooks 의존성 제거

  // 겨울방학 추천 도서 로드 (초기 데이터 없으면 로드)
  /* 
  useEffect(() => {
    if (winterBooks.length === 0) {
      getWinterBooks(7).then(setWinterBooks)
    }
  }, []) // winterBooks 의존성 제거
  */

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      sendGAEvent('home_search', { keyword: searchQuery })
      router.push(`/books?q=${encodeURIComponent(searchQuery)}`)
    } else {
      router.push('/books')
    }
  }

  return (
    <main className="min-h-screen bg-[#F7F7F7]">
      <header className="w-full bg-white border-b border-gray-100 flex items-center justify-center px-6 py-4 sticky top-0 z-50 relative">
        {/* 로고 중앙 정렬 */}
        <h1>
          <button
            onClick={() => router.push('/')}
            className="relative inline-flex items-center cursor-pointer"
          >
            <img
              src="/logo.png"
              alt="책자리"
              className="h-9 w-auto"
            />
            <span className="absolute top-1 -right-9 text-gray-400 text-xs font-bold leading-none italic">
              beta
            </span>
          </button>
        </h1>

        {/* 도서관 선택 버튼 숨김 처리 */}
        {/* <LibrarySelector /> */}

        {user ? (
          <div className="absolute right-6 flex items-center gap-3 md:gap-4">
            <button
              onClick={() => {
                const searchEl = document.getElementById('global-search-bar');
                if (searchEl) {
                  searchEl.classList.toggle('hidden');
                  searchEl.querySelector('input')?.focus();
                }
              }}
              className="text-gray-500 p-1"
              aria-label="검색 열기"
            >
              <Search className="w-5 h-5" />
            </button>
            <button
              onClick={() => router.push('/my-page')}
              className="p-1 flex items-center justify-center group"
              aria-label="마이 페이지"
            >
              <UserAvatar user={user} size={24} className="text-gray-500" />
            </button>
          </div>
        ) : (
          <div className="absolute right-6 flex items-center gap-3 md:gap-4">
            <button
              onClick={() => {
                const searchEl = document.getElementById('global-search-bar');
                if (searchEl) {
                  searchEl.classList.toggle('hidden');
                  searchEl.querySelector('input')?.focus();
                }
              }}
              className="text-gray-500 p-1"
              aria-label="검색 열기"
            >
              <Search className="w-5 h-5" />
            </button>
            <button
              onClick={() => router.push('/auth/signup')}
              className="p-1 flex items-center justify-center group"
              aria-label="로그인"
            >
              <UserAvatar user={null} size={24} className="text-gray-500" />
            </button>
          </div>
        )}
      </header>


      {/* 메인 배너 */}
      {/* <MainBanner /> */}

      {/* 검색 바 - 숨겨져 있다가 토글됨 */}
      <div id="global-search-bar" className="w-full hidden sticky top-[73px] z-20 bg-[#F7F7F7]/95 backdrop-blur-sm px-4 py-3 transition-all border-b border-gray-100">
        <form onSubmit={handleSearch} className="w-full max-w-[1200px] mx-auto flex gap-3">
          <div className="relative group flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="어떤 책을 찾으시나요?"
              className="w-full px-4 py-2.5 pr-10 bg-white text-gray-900 placeholder:text-gray-400 border border-transparent rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-[#F59E0B]/20 transition-all text-sm"
            />

            {/* Clear button */}
            {searchQuery && <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 p-1"
                  aria-label="검색어 지우기"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              }
            </div>
          </form>
      </div>


      {/* 1. 우리 아이 나이에 딱! (연령별 추천 섹션) */}
      <section className="py-8 px-4 bg-white">
        <div className="max-w-[1200px] mx-auto">
          <div className="flex items-center justify-between mb-1 px-2">
            <h2 className="text-xl font-bold text-gray-900">우리 아이 나이에 딱!</h2>
            <Link
              href={`/books?age=${selectedAge}`}
              className="text-gray-900"
              onClick={() => sendGAEvent('click_view_more', { section: 'age_recommendation', age: selectedAge })}
            >
              <ChevronRight className="w-6 h-6" />
            </Link>
          </div>

          <div className="px-2 mb-4">
            <p className="text-sm text-gray-600">발달 단계에 맞는 맞춤 도서를 만나보세요</p>
          </div>

          {/* 연령 탭 */}
          <div className="flex gap-2 mb-6 px-2">
            {[
              { key: '0-3', label: '0~3세' },
              { key: '4-7', label: '4~7세' },
              { key: '8-12', label: '8~12세' },
              { key: 'teen', label: '13세 이상' }
            ].map(age => (
              <button
                key={age.key}
                onClick={() => {
                  setSelectedAge(age.key);
                  sendGAEvent('click_home_age_tab', { age: age.key });
                }}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${selectedAge === age.key
                  ? 'bg-brand-primary text-white'
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
                {[1, 2, 3, 4, 5, 6, 7].map((i, index, array) => (
                  <div key={i} className={`flex-shrink-0 w-[160px] sm:w-[180px] ${index === array.length - 1 ? 'mr-4' : ''}`}>
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
                    <div key={book.id} className={`flex-shrink-0 w-[160px] sm:w-[180px] ${index === ageBooks.length - 1 ? 'mr-4' : ''}`}>
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

      {/* 2. 칼데콧 수상작 섹션 */}
      <section className="py-8 px-4">
        <div className="max-w-[1200px] mx-auto">
          <div className="flex items-center justify-between mb-1 px-2">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <span>칼데콧 수상작</span>
            </h2>
            <Link
              href="/books?curation=caldecott"
              className="text-gray-900 hover:text-gray-600 transition-colors"
              onClick={() => sendGAEvent('click_view_more', { section: 'caldecott' })}
            >
              <ChevronRight className="w-6 h-6" />
            </Link>
          </div>

          <div className="px-2 mb-4">
            <p className="text-sm text-gray-600">미국 도서관 사서들이 엄선한 최고의 그림책</p>
          </div>

          {caldecottBooks.length > 0 ? (
            <div className="overflow-x-auto scrollbar-hide -mx-4 px-4">
              <div className="flex gap-4 pb-2">
                {caldecottBooks.map((book, index) => (
                  <div key={book.id} className={`flex-shrink-0 w-[160px] sm:w-[180px] ${index === caldecottBooks.length - 1 ? 'mr-4' : ''}`}>
                    <BookCard book={book} />
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              수상작 목록을 불러오는 중입니다...
            </div>
          )}
        </div>
      </section>

      {/* 3. 도서 연구회 추천 섹션 */}
      <section className="py-8 px-4 bg-white">
        <div className="max-w-[1200px] mx-auto">
          <div className="flex items-center justify-between mb-1 px-2">
            <h2 className="text-xl font-bold text-gray-900">어린이 도서 연구회 추천</h2>
            <Link
              href="/books?curation=research-council"
              className="text-gray-900 hover:text-gray-600 transition-colors"
              onClick={() => sendGAEvent('click_view_more', { section: 'research_council' })}
            >
              <ChevronRight className="w-6 h-6" />
            </Link>
          </div>

          <div className="px-2 mb-4">
            <p className="text-sm text-gray-600">전문가가 엄선한 믿고 보는 필독서</p>
          </div>

          {researchBooks.length > 0 ? (
            <>
              <div className="overflow-x-auto scrollbar-hide -mx-4 px-4">
                <div className="flex gap-4 pb-2">
                  {researchBooks.map((book, index) => (
                    <div key={book.id} className={`flex-shrink-0 w-[160px] sm:w-[180px] ${index === researchBooks.length - 1 ? 'mr-4' : ''}`}>
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
      </section >

      {/* 겨울방학 추천 섹션 (주석 처리) */}
      {/* 
      <section className="py-8 px-4 bg-white">
        <div className="max-w-[1200px] mx-auto">
          <div className="flex items-center justify-between mb-1 px-2">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <span>사서 추천 겨울방학 도서</span>
            </h2>
            <Link
              href="/books?curation=winter-vacation"
              className="text-gray-900 hover:text-gray-600 transition-colors"
            >
              <ChevronRight className="w-6 h-6" />
            </Link>
          </div>

          <div className="px-2 mb-4">
            <p className="text-sm text-gray-600">긴 방학, 스마트폰 대신 책과 친해져요</p>
          </div>

          {winterBooks.length > 0 ? (
            <div className="overflow-x-auto scrollbar-hide -mx-4 px-4">
              <div className="flex gap-4 pb-2">
                {winterBooks.map((book, index) => (
                  <div key={book.id} className={`flex-shrink-0 w-[160px] sm:w-[180px] ${index === winterBooks.length - 1 ? 'mr-4' : ''}`}>
                    <BookCard book={book} />
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-[280px] flex items-center justify-center">
              <div className="animate-pulse flex gap-4 overflow-hidden w-full">
                {[1, 2, 3, 4, 5, 6, 7].map(i => (
                  <div key={i} className="w-[160px] h-[240px] bg-gray-200 rounded-lg flex-shrink-0" />
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
      */}

      {/* 디바이더 */}
      < div className="border-t border-gray-200" ></div >

      {/* 공지사항 섹션 */}
      < section className="py-6 px-4 bg-white" >
        <div className="max-w-6xl mx-auto">
          <a
            href="https://amplified-decimal-9c4.notion.site/26-01-10-2e4939f003ba80f2b698e9e016910587?source=copy_link"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 text-gray-700 hover:text-gray-900 transition-colors group"
          >
            <Bell className="w-5 h-5 text-[#F59E0B] group-hover:text-[#D97706] transition-colors" />
            <span className="text-sm font-medium">서비스 오픈 안내(1/10)</span>
          </a>
        </div>
      </section >

      <Footer />

      {/* 회원 탈퇴 완료 팝업 */}
      <ConfirmModal
        isOpen={isWithdrawnPopupOpen}
        onClose={() => setIsWithdrawnPopupOpen(false)}
        onConfirm={() => setIsWithdrawnPopupOpen(false)}
        title="회원 탈퇴 완료"
        description={
          <div className="text-gray-600 leading-relaxed text-center break-keep">
            회원 탈퇴가 완료되었습니다.<br />
            아이와 도서관 나들이가 생각날 때<br />
            언제든 다시 책자리를 찾아주세요.
          </div>
        }
        confirmLabel="확인"
        cancelLabel=""
        confirmVariant="primary"
      />

      {/* 회원가입 완료 팝업 */}
      <ConfirmModal
        isOpen={isSignupCompleteOpen}
        onClose={() => setIsSignupCompleteOpen(false)}
        onConfirm={() => setIsSignupCompleteOpen(false)}
        title="회원 가입 완료"
        description={
          <div className="text-gray-600 leading-relaxed text-center break-keep">
            책자리 회원 가입이 완료되었습니다.<br />
            우리 아이에게 딱 맞는 책,<br />
            지금 바로 찾아보세요.
          </div>
        }
        confirmLabel="확인"
        cancelLabel=""
        confirmVariant="primary"
        hideOverlay
      />

      {/* 하단 토스트 팝업 */}
      <Toast
        message={logoutToastMessage}
        isVisible={!!logoutToastMessage}
        onClose={() => setLogoutToastMessage('')}
      />
    </main >
  )
}

// 책 카드 컴포넌트 - BookItem과 동일한 UI
function BookCard({ book }: { book: Book }) {

  const displayAge = getAgeDisplayLabel(book.age)

  // 청구기호 결정 로직 (판교도서관 고정)
  let displayCallNo = ''
  if (book.pangyo_callno && book.pangyo_callno !== '없음') {
    displayCallNo = book.pangyo_callno
  } else {
    const info = book.library_info?.find((l: LibraryInfo) => l.library_name.includes('판교'))
    if (info) displayCallNo = info.callno
  }

  return (
    <Link
      href={`/book/${book.id}`}
      className="flex flex-col bg-white rounded-lg border border-gray-100 overflow-hidden transition-all h-full group"
    >
      {/* 1. 이미지 영역 (상단) */}
      <div className="relative w-full aspect-[1/1.1] bg-[#F9FAFB] overflow-hidden flex items-center justify-center">
        {book.image_url ? (
          <img
            src={book.image_url}
            alt={book.title}
            className="w-full h-full object-cover"
            loading="eager"
            fetchPriority="high"
          />
        ) : (
          <div className="flex flex-col items-center justify-center w-full h-full text-gray-300">
            <BookOpen className="w-12 h-12 opacity-20" />
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
        <h3 className="text-base font-bold text-gray-900 leading-[1.35] mb-1.5 line-clamp-2 tracking-tight">
          {book.title}
        </h3>

        <p className={`text-[15px] font-extrabold tracking-tight mb-3 truncate w-full ${!displayCallNo ? 'text-gray-300' : 'text-[#F59E0B]'}`}>
          {displayCallNo}
        </p>

        <div className="mt-auto pt-3 border-t border-gray-50 w-full flex items-center justify-between text-xs font-medium">
          <span className="text-gray-400 truncate max-w-[60%]">{book.publisher}</span>
        </div>
      </div>
    </Link>
  )
}
