'use client'

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@/context/AuthContext'
import { supabase } from '@/lib/supabase'
import { getSavedBookIds } from '@/lib/supabase-api'
import { getBooksByIds, fetchLoanStatuses, getMyRatedBooks } from '@/lib/api'
import { useLibrary } from '@/context/LibraryContext'
import LibrarySelector from '@/components/LibrarySelector'
import { Book, RatedBook } from '@/lib/types'
import BookItem from '@/components/BookItem'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ProfileDropdown from '@/components/ProfileDropdown'
import PageHeader from '@/components/PageHeader'
import { PageLoader } from '@/components/ui/PageLoader'
import { Star } from 'lucide-react'
import Image from 'next/image'

type Tab = 'saved' | 'rated'

export default function MyLibraryPage() {
    const { user, isLoading: authLoading } = useAuth()
    const { selectedLibrary } = useLibrary()
    const router = useRouter()

    const [activeTab, setActiveTab] = useState<Tab>('saved')

    // 저장한 책
    const [savedBooks, setSavedBooks] = useState<Book[]>([])
    const [isSavedLoading, setIsSavedLoading] = useState(true)

    // 별점 남긴 책
    const [ratedBooks, setRatedBooks] = useState<RatedBook[]>([])
    const [isRatedLoading, setIsRatedLoading] = useState(false)
    const [ratedLoaded, setRatedLoaded] = useState(false)

    // 비로그인 → 홈 리다이렉트
    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/')
        }
    }, [user, authLoading, router])

    // 저장한 책 로드
    useEffect(() => {
        const fetchSavedBooks = async () => {
            if (!user) return
            setIsSavedLoading(true)
            try {
                const savedIds = await getSavedBookIds(supabase, user.id)
                if (savedIds.length === 0) {
                    setSavedBooks([])
                    return
                }
                const booksData = await getBooksByIds(savedIds)
                setSavedBooks(booksData)

                const loanStatuses = selectedLibrary
                    ? await fetchLoanStatuses(savedIds, selectedLibrary)
                    : {}
                setSavedBooks(booksData.map(book => ({
                    ...book,
                    loan_status: loanStatuses[book.id] || null
                })))
            } catch (err) {
                console.error('저장한 책 조회 실패:', err)
            } finally {
                setIsSavedLoading(false)
            }
        }

        if (user) fetchSavedBooks()
    }, [user, selectedLibrary])

    // 별점 남긴 책 로드 (탭 전환 시 최초 1회)
    const fetchRatedBooks = useCallback(async () => {
        if (!user || ratedLoaded) return
        setIsRatedLoading(true)
        try {
            const { data: { session } } = await supabase.auth.getSession()
            if (!session?.access_token) return
            const res = await getMyRatedBooks(session.access_token)
            setRatedBooks(res.rated_books)
            setRatedLoaded(true)
        } catch (err) {
            console.error('별점 남긴 책 조회 실패:', err)
        } finally {
            setIsRatedLoading(false)
        }
    }, [user, ratedLoaded])

    useEffect(() => {
        if (activeTab === 'rated') fetchRatedBooks()
    }, [activeTab, fetchRatedBooks])

    const isInitialLoading = authLoading || (isSavedLoading && savedBooks.length === 0 && activeTab === 'saved')
    if (isInitialLoading) return <PageLoader />

    return (
        <main className="min-h-screen bg-[#F7F7F7]">
            <PageHeader title="내 책장" showHome={true} rightSlot={<ProfileDropdown />} />

            {/* 탭 */}
            <div className="bg-white border-b border-gray-200">
                <div className="max-w-[480px] mx-auto flex">
                    <button
                        onClick={() => setActiveTab('saved')}
                        className={`flex-1 py-3 text-sm font-semibold transition-colors ${
                            activeTab === 'saved'
                                ? 'text-gray-900 border-b-2 border-[#F59E0B]'
                                : 'text-gray-400'
                        }`}
                    >
                        저장한 책
                    </button>
                    <button
                        onClick={() => setActiveTab('rated')}
                        className={`flex-1 py-3 text-sm font-semibold transition-colors ${
                            activeTab === 'rated'
                                ? 'text-gray-900 border-b-2 border-[#F59E0B]'
                                : 'text-gray-400'
                        }`}
                    >
                        별점 남긴 책
                    </button>
                </div>
            </div>

            {/* 저장한 책 탭 */}
            {activeTab === 'saved' && (
                <div className="max-w-7xl mx-auto px-6 py-6">
                    <div className="mb-6 flex items-center justify-between border-b border-gray-100 pb-4">
                        <p className="text-gray-500 font-medium">총 {savedBooks.length}권</p>
                        {selectedLibrary ? (
                            <LibrarySelector
                                customTrigger={(open) => (
                                    <button
                                        onClick={open}
                                        className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 transition-colors"
                                    >
                                        <span>기준 도서관: <span className="font-semibold text-gray-600">{selectedLibrary}</span></span>
                                        <svg className="w-3.5 h-3.5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                                            <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                                        </svg>
                                    </button>
                                )}
                            />
                        ) : (
                            <LibrarySelector
                                customTrigger={(open) => (
                                    <button
                                        onClick={open}
                                        className="text-sm text-gray-400 underline underline-offset-2 decoration-gray-300"
                                    >
                                        도서관 설정하기
                                    </button>
                                )}
                            />
                        )}
                    </div>

                    {savedBooks.length === 0 ? (
                        <div className="py-20 flex flex-col items-center justify-center text-center">
                            <p className="text-gray-600 font-bold text-lg mb-1">아직 담아둔 책이 없어요</p>
                            <p className="text-gray-400 text-sm mb-6">책을 담고 청구기호를 한눈에 확인해 보세요</p>
                            <Link
                                href="/"
                                className="px-6 py-3 bg-[#F59E0B] text-white rounded-lg font-semibold transition-all"
                            >
                                책 보러 가기
                            </Link>
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                            {savedBooks.map((book) => (
                                <BookItem key={book.id} book={book} loanStatus={book.loan_status ?? undefined} showLibraryInfo={true} />
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* 별점 남긴 책 탭 */}
            {activeTab === 'rated' && (
                <div className="max-w-7xl mx-auto px-6 py-6">
                    {isRatedLoading ? (
                        <div className="py-20 flex items-center justify-center">
                            <PageLoader />
                        </div>
                    ) : ratedBooks.length === 0 ? (
                        <div className="py-20 flex flex-col items-center justify-center text-center">
                            <p className="text-gray-600 font-bold text-lg mb-1">아직 별점을 남긴 책이 없어요</p>
                            <p className="text-gray-400 text-sm mb-6">도서 상세 페이지에서 별점을 남겨보세요</p>
                            <Link
                                href="/"
                                className="px-6 py-3 bg-[#F59E0B] text-white rounded-lg font-semibold transition-all"
                            >
                                책 보러 가기
                            </Link>
                        </div>
                    ) : (
                        <>
                            <p className="text-gray-500 font-medium mb-6 border-b border-gray-100 pb-4">
                                총 {ratedBooks.length}권
                            </p>
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                                {ratedBooks.map((book) => (
                                    <RatedBookCard key={book.review_id} book={book} />
                                ))}
                            </div>
                        </>
                    )}
                </div>
            )}
        </main>
    )
}

function RatedBookCard({ book }: { book: RatedBook }) {
    return (
        <Link href={`/book/${book.id}`} className="group block">
            <div className="relative bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] overflow-hidden active:scale-[0.98] transition-transform">
                {/* 표지 */}
                <div className="relative w-full aspect-[1/1.1] bg-gray-100">
                    {book.image_url ? (
                        <Image
                            src={book.image_url}
                            alt={book.title}
                            fill
                            className="object-cover"
                            sizes="(max-width: 768px) 50vw, 25vw"
                        />
                    ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gray-200">
                            <span className="text-gray-400 text-xs">표지 없음</span>
                        </div>
                    )}
                    {/* 별점 오버레이 */}
                    <div className="absolute bottom-0 left-0 right-0 bg-black/60 py-1.5 px-2 flex items-center gap-1">
                        <Star className="w-3.5 h-3.5 fill-[#F59E0B] text-[#F59E0B]" />
                        <span className="text-white text-xs font-bold">{book.rating.toFixed(1)}</span>
                    </div>
                </div>

                {/* 정보 */}
                <div className="p-3">
                    <p className="text-gray-900 text-sm font-semibold line-clamp-2 leading-tight mb-1">
                        {book.title}
                    </p>
                    {book.publisher && (
                        <p className="text-gray-400 text-xs truncate">{book.publisher}</p>
                    )}
                </div>
            </div>
        </Link>
    )
}
