'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import { createClient } from '@/lib/supabase'
import { saveBook, unsaveBook } from '@/lib/supabase-api'
import { getBookById, fetchLoanStatuses } from '@/lib/api'
import { Book } from '@/lib/types'
import {
    Heart,
    ChevronLeft,
    Loader2,
    BookOpen,
    MapPin,
    User as UserIcon,
    Building2,
    Tags,
    Share2
} from 'lucide-react'
import Link from 'next/link'

export default function BookDetailPage() {
    const { id } = useParams()
    const router = useRouter()
    const { user } = useAuth()
    const [book, setBook] = useState<Book | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isSaved, setIsSaved] = useState(false)
    const [saveCount, setSaveCount] = useState(0)
    const [isToggling, setIsToggling] = useState(false)

    const supabase = createClient()

    useEffect(() => {
        const fetchDetail = async () => {
            if (!id) return
            setIsLoading(true)
            try {
                const bookId = parseInt(id as string)
                const data = await getBookById(bookId)
                if (!data) {
                    setBook(null)
                    setIsLoading(false)
                    return
                }

                // Display book immediately without loan status
                setBook(data)
                setSaveCount(data.save_count || 0)
                setIsLoading(false)

                // Fetch loan status in background (progressive loading)
                fetchLoanStatuses([bookId])
                    .then(loanStatuses => {
                        setBook(prev => prev ? {
                            ...prev,
                            loan_status: loanStatuses[bookId] || null
                        } : null)
                    })
                    .catch(err => {
                        console.error('Failed to fetch loan status:', err)
                    })

                // Check if saved
                if (user) {
                    const { data: savedData } = await supabase
                        .from('user_saved_books')
                        .select('id')
                        .match({ user_id: user.id, book_id: bookId })
                        .maybeSingle()

                    if (savedData) setIsSaved(true)
                }
            } catch (err) {
                console.error('Failed to fetch book detail:', err)
                setIsLoading(false)
            }
        }

        fetchDetail()
    }, [id, user, supabase])

    const handleToggleSave = async () => {
        if (!user) {
            alert('베타 기간에는 로그인/회원가입 기능을 제공하지 않습니다.');
            return
        }

        if (!book || isToggling) return
        setIsToggling(true)
        try {
            if (isSaved) {
                await unsaveBook(supabase, user.id, book.id)
                setIsSaved(false)
                setSaveCount(prev => Math.max(0, prev - 1))
            } else {
                await saveBook(supabase, user.id, book.id)
                setIsSaved(true)
                setSaveCount(prev => prev + 1)
            }
        } catch (err) {
            console.error('Failed to toggle save:', err)
        } finally {
            setIsToggling(false)
        }
    }

    if (isLoading) {
        return (
            <div className="min-h-screen bg-white flex flex-col items-center justify-center">
                <Loader2 className="w-10 h-10 text-blue-600 animate-spin mb-4" />
                <p className="text-gray-500 font-medium">책 정보를 불러오는 중...</p>
            </div>
        )
    }

    if (!book) {
        return (
            <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6 text-center">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">책을 찾을 수 없습니다</h2>
                <Link href="/" className="text-blue-600 font-bold">메인으로 돌아가기</Link>
            </div>
        )
    }

    return (
        <main className="min-h-screen bg-white pb-20">
            {/* Top Header */}
            <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100 px-6 py-4 flex items-center justify-between">
                <button onClick={() => router.back()} className="p-2 -ml-2 text-gray-500 hover:text-gray-900">
                    <ChevronLeft className="w-6 h-6" />
                </button>
                <h1 className="text-sm font-bold text-gray-900 truncate max-w-[200px]">상세 정보</h1>
                <div className="w-10" />
            </header>

            <div className="max-w-4xl mx-auto px-6 pt-8">
                <div className="flex flex-col md:flex-row gap-8 md:items-start max-w-5xl mx-auto">
                    {/* Left: Image Card - Reduced width to approx 70% of original (50% -> 35%) */}
                    <div className="w-full md:w-[35%] shrink-0 max-w-[320px] mx-auto md:mx-0">
                        <div className="relative aspect-[3/4] bg-gray-50 rounded-[28px] overflow-hidden shadow-2xl shadow-gray-200 border border-gray-100">
                            {book.image_url ? (
                                <img src={book.image_url} alt={book.title} className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-gray-300">
                                    <BookOpen className="w-16 h-16 opacity-20" />
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right: Info Area */}
                    <div className="w-full md:w-[65%] flex flex-col pt-1">
                        <div className="mb-4">
                            {/* Tags Row */}
                            <div className="flex flex-wrap gap-2 mb-3">
                                {book.category && (
                                    <span className="px-2.5 py-0.5 bg-blue-50 text-blue-600 rounded-lg text-[11px] font-bold border border-blue-100">
                                        {book.category}
                                    </span>
                                )}
                                {book.age && (
                                    <span className="px-2.5 py-0.5 bg-amber-50 text-amber-600 rounded-lg text-[11px] font-bold border border-amber-100">
                                        {book.age}
                                    </span>
                                )}
                            </div>

                            <h2 className="text-xl md:text-2xl font-black text-gray-900 leading-tight mb-2 tracking-tight">
                                {book.title}
                            </h2>

                            <div className="flex flex-col gap-0.5 text-gray-600 font-medium text-base mb-8">
                                <span>{book.author || '정보 없음'}</span>
                                <span className="text-gray-400 text-sm">{book.publisher || '정보 없음'}</span>
                            </div>

                            <div className="mb-2">
                                <span className="text-sm text-gray-600 block mb-1.5 flex items-center gap-1">
                                    <MapPin className="w-3.5 h-3.5" />
                                    판교 도서관
                                </span>
                                <div className="flex items-center gap-3">
                                    <span className="font-black text-2xl text-gray-900 tracking-tight">
                                        {book.pangyo_callno}{book.vol ? `-${book.vol}` : ''}
                                    </span>
                                    {book.loan_status ? (
                                        <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${book.loan_status.available
                                            ? "bg-green-50 text-green-700 border-green-200"
                                            : "bg-red-50 text-red-700 border-red-200"
                                            }`}>
                                            {book.loan_status.status}
                                        </span>
                                    ) : (
                                        <span className="px-2.5 py-1 rounded-lg text-xs bg-gray-100 text-gray-400 border border-gray-200 animate-pulse">
                                            확인중
                                        </span>
                                    )}
                                </div>
                                <a
                                    href="https://docs.google.com/forms/d/e/1FAIpQLSflKo4QGT_7DUZiwq-w_5lo2ubEDQtJqVsGeX2fsp5P778vhQ/viewform?usp=dialog"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-gray-400 hover:text-gray-600 underline mt-1.5 inline-block"
                                >
                                    청구기호 다른가요?
                                </a>
                            </div>
                        </div>

                        {/* Save & Share Area */}
                        <div className="mt-2 pt-6 border-t border-gray-100 flex gap-3">
                            <button
                                onClick={handleToggleSave}
                                disabled={isToggling}
                                className={`w-14 h-14 rounded-lg flex items-center justify-center transition-all transform active:scale-[0.98] border ${isSaved
                                    ? "bg-amber-50 text-[#F59E0B] border-amber-200 shadow-lg shadow-gray-200"
                                    : "bg-white text-gray-400 border-gray-100 hover:bg-gray-50"
                                    }`}
                                title={isSaved ? "찜 취소" : "찜하기"}
                            >
                                <Heart className={`w-6 h-6 ${isSaved ? "fill-current" : ""}`} />
                            </button>
                            <button className="w-14 h-14 flex items-center justify-center bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition-colors border border-gray-100">
                                <Share2 className="w-6 h-6" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Book Description Section */}
            <div className="mt-12 max-w-4xl mx-auto px-6">
                <h3 className="text-lg font-black text-gray-900 mb-4 flex items-center gap-2">
                    <div className="w-1.5 h-6 bg-orange-500 rounded-full" />
                    도서 소개
                </h3>
                <div className="text-gray-600 leading-relaxed text-sm md:text-base font-medium">
                    {book.description ? (
                        <div
                            dangerouslySetInnerHTML={{ __html: book.description }}
                            className="prose prose-sm max-w-none prose-p:mb-3 prose-strong:text-orange-600"
                        />
                    ) : (
                        <p className="text-gray-400 italic">등록된 도서 소개 정보가 없습니다.</p>
                    )}
                </div>
            </div>
        </main>
    )
}
