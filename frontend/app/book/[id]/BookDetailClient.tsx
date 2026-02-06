'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import { createClient } from '@/lib/supabase'
import { saveBook, unsaveBook } from '@/lib/supabase-api'
import { fetchLoanStatuses } from '@/lib/api'
import { Book, LoanStatus } from '@/lib/types'
import {
    Heart,
    ChevronLeft,
    Loader2,
    BookOpen,
    MapPin,
    Share2,
    ShoppingCart
} from 'lucide-react'
import Link from 'next/link'
import LibrarySelector from '@/components/LibrarySelector'
import { useLibrary } from '@/context/LibraryContext'
import { sendGAEvent } from '@/lib/analytics'

interface BookDetailClientProps {
    book: Book
}

export default function BookDetailClient({ book: initialBook }: BookDetailClientProps) {
    const router = useRouter()
    const { user } = useAuth()
    const [book, setBook] = useState<Book>(initialBook)
    const [isSaved, setIsSaved] = useState(false)
    const [saveCount, setSaveCount] = useState(initialBook.save_count || 0)
    const [isToggling, setIsToggling] = useState(false)
    const [imageError, setImageError] = useState(false)
    const { selectedLibrary } = useLibrary()

    // Handle book navigation
    useEffect(() => {
        setBook(initialBook)
        setSaveCount(initialBook.save_count || 0)
        setImageError(false)
        setIsSaved(false)
    }, [initialBook])

    const supabase = createClient()

    // 청구기호 결정 로직
    let displayCallNo = '청구기호 없음'
    if (selectedLibrary === '판교도서관') {
        if (book.pangyo_callno && book.pangyo_callno !== '없음') {
            displayCallNo = book.pangyo_callno
        } else {
            const info = book.library_info?.find(l => l.library_name.includes('판교'))
            if (info) displayCallNo = info.callno
        }
    } else {
        const info = book.library_info?.find(l => l.library_name === selectedLibrary || l.library_name.includes(selectedLibrary))
        if (info) {
            displayCallNo = info.callno
        } else {
            displayCallNo = '보유 정보 없음'
        }
    }

    // React Query for Loan Status
    const { data: loanStatuses, isError: isLoanError } = useQuery({
        queryKey: ['book-loan-status', book.id],
        queryFn: async () => {
            return await fetchLoanStatuses([book.id]);
        },
        enabled: !!displayCallNo && displayCallNo !== '청구기호 없음' && displayCallNo !== '보유 정보 없음',
        staleTime: 5 * 60 * 1000,
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        refetchOnWindowFocus: false,
    });

    // Derive final status
    const normalizedStatus = (() => {
        // 1. 청구기호 없으면 무조건 '미소장'
        if (!displayCallNo || displayCallNo === '청구기호 없음' || displayCallNo === '보유 정보 없음') {
            return { status: "미소장", available: null };
        }

        const rawStatus = loanStatuses?.[book.id];
        if (rawStatus) {
            const status = rawStatus.status;
            if (status === "시간초과") return { ...rawStatus, status: "확인불가", available: null };
            if (status === "정보없음") return { ...rawStatus, status: "확인중", available: null };
            if (status === "미소장") return { ...rawStatus, status: "확인중", available: null };
            return rawStatus;
        }

        if (isLoanError) {
            return { status: "확인중", available: null };
        }

        return undefined;
    })();

    // Send GA event when book detail page is viewed
    useEffect(() => {
        sendGAEvent('view_book_detail', {
            book_id: book.id,
            book_title: book.title,
            call_number: displayCallNo,
            category: book.category,
            age: book.age
        });
    }, [book.id]);

    // Check if book is saved
    useEffect(() => {
        const checkSaved = async () => {
            if (user) {
                const { data: savedData } = await supabase
                    .from('user_saved_books')
                    .select('id')
                    .match({ user_id: user.id, book_id: book.id })
                    .maybeSingle()

                if (savedData) setIsSaved(true)
            }
        }
        checkSaved()
    }, [user, book.id, supabase])

    const handleToggleSave = async () => {
        if (!user) {
            alert('베타 기간에는 로그인/회원가입 기능을 제공하지 않습니다.')
            return
        }

        if (isToggling) return
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
            // GA Event
            sendGAEvent('toggle_save_book', {
                book_id: book.id,
                book_title: book.title,
                state: !isSaved ? 'save' : 'unsave' // Logic inverted because state hasn't updated in this closure yet? verify logic.
                // Actually isSaved is the OLD state. 
                // If isSaved was true, we unsaved. New state is 'unsave'.
                // If isSaved was false, we saved. New state is 'save'.
            })
        }
    }

    const handleShare = async () => {
        const shareData = {
            title: book.title,
            text: `${book.title} - 이 책, 지금 도서관에 있을까? 헛걸음 전 3초 확인!`,
            url: window.location.href
        }

        try {
            if (typeof navigator.share === 'function') {
                await navigator.share(shareData)
            } else {
                await navigator.clipboard.writeText(window.location.href)
                alert('링크가 클립보드에 복사되었습니다!')
            }
        } catch (err) {
            console.error('Share failed:', err)
        } finally {
            sendGAEvent('share_book', {
                book_id: book.id,
                book_title: book.title,
                method: typeof navigator.share === 'function' ? 'native_share' : 'clipboard'
            })
        }


    }

    const generateKyoboDeepLink = (isbn: string) => {
        // 교보문고 상품 상세 URL로 직접 이동이 불가하여(Internal ID 필요), 검색 결과 페이지로 랜딩
        const targetUrl = `https://search.kyobobook.co.kr/search?keyword=${isbn}&gbCode=TOT&target=total`
        const encodedTargetUrl = encodeURIComponent(targetUrl)

        // LinkPrice Deep Link (Corrected based on sample)
        // m: merchant id (kbbook)
        // a: affiliate id (A100702199)
        // l: link id (9999)
        // l_cd1: 3, l_cd2: 0
        // tu: target url
        return `https://linkmoa.kr/click.php?m=kbbook&a=A100702199&l=9999&l_cd1=3&l_cd2=0&tu=${encodedTargetUrl}`
    }

    const handleBuyKyobo = () => {
        if (!book.isbn) {
            alert('ISBN 정보가 없어 구매 페이지로 이동할 수 없습니다.')
            return
        }

        const deepLink = generateKyoboDeepLink(book.isbn)

        sendGAEvent('click_buy_kyobo', {
            book_id: book.id,
            book_title: book.title,
            isbn: book.isbn,
            link_type: 'deep_link'
        })

        window.open(deepLink, '_blank')
    }

    return (
        <main className="min-h-screen bg-white pb-20">
            {/* Top Header */}
            <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <button onClick={() => router.back()} className="p-2 -ml-2 text-gray-500 hover:text-gray-900">
                        <ChevronLeft className="w-6 h-6" />
                    </button>
                    <span className="text-base font-bold text-gray-900 truncate max-w-[200px]">도서 정보</span>
                </div>
                {/* <LibrarySelector /> */}
            </header>

            <div className="max-w-4xl mx-auto px-6 pt-8">
                <div className="flex flex-col md:flex-row gap-8 md:items-start max-w-5xl mx-auto">
                    {/* Left: Image Card */}
                    <div className="w-full md:w-[35%] shrink-0 max-w-[320px] mx-auto md:mx-0">
                        <div className="relative aspect-[3/4] bg-gray-50 rounded-[28px] overflow-hidden shadow-2xl shadow-gray-200 border border-gray-100">
                            {book.image_url && !imageError ? (
                                <img
                                    src={book.image_url}
                                    alt={`${book.title} 표지`}
                                    className="w-full h-full object-cover"
                                    onError={() => setImageError(true)}
                                />
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

                            <h1 className="text-xl md:text-2xl font-black text-gray-900 leading-tight mb-2 tracking-tight line-clamp-3">
                                {book.title}
                            </h1>

                            <div className="flex flex-col gap-0.5 text-gray-600 font-medium text-base mb-8">
                                <span>{book.author || '정보 없음'}</span>
                                <span className="text-gray-400 text-sm">{book.publisher || '정보 없음'}</span>
                            </div>

                            <div className="mb-2">
                                <span className="text-sm text-gray-600 block mb-1.5 flex items-center gap-1">
                                    <MapPin className="w-3.5 h-3.5" />
                                    {selectedLibrary}
                                </span>
                                <div className="flex items-center gap-3">
                                    <span className={`font-black text-2xl tracking-tight ${displayCallNo === '보유 정보 없음' ? 'text-gray-300' : 'text-gray-900'}`}>
                                        {displayCallNo}{book.vol ? `-${book.vol}` : ''}
                                    </span>
                                    {normalizedStatus && (
                                        <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${normalizedStatus.available === true
                                            ? "bg-green-50 text-green-700 border-green-200"
                                            : normalizedStatus.available === false
                                                ? "bg-red-50 text-red-700 border-red-200"
                                                : normalizedStatus.status === "미소장"
                                                    ? "bg-gray-100 text-gray-700 border-gray-200"
                                                    : normalizedStatus.status === "확인중"
                                                        ? "bg-orange-50 text-orange-600 border-orange-200"
                                                        : "bg-white text-gray-600 border-gray-300"
                                            }`}>
                                            {normalizedStatus.status}
                                        </span>
                                    )}
                                </div>
                                <a
                                    href="https://docs.google.com/forms/d/e/1FAIpQLSflKo4QGT_7DUZiwq-w_5lo2ubEDQtJqVsGeX2fsp5P778vhQ/viewform?usp=dialog"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-gray-400 hover:text-gray-600 underline mt-1.5 inline-block"
                                    onClick={() => sendGAEvent('click_report_error', { book_id: book.id })}
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
                            <button
                                onClick={handleShare}
                                className="w-14 h-14 flex items-center justify-center bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition-colors border border-gray-100 active:scale-[0.98] transform"
                                title="공유하기"
                            >
                                <Share2 className="w-6 h-6" />
                            </button>
                            <button
                                onClick={handleBuyKyobo}
                                className="flex-1 h-14 bg-[#F59E0B] text-white rounded-lg font-bold text-base flex items-center justify-center gap-2 hover:bg-[#D97706] focus:bg-[#F59E0B] focus:outline-none transition-colors"
                            >
                                <ShoppingCart className="w-5 h-5" />
                                도서 구매하기
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
        </main >
    )
}
