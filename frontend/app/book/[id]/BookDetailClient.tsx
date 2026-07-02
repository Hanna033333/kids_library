'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import { supabase } from '@/lib/supabase'
import { saveBook, unsaveBook } from '@/lib/supabase-api'
import { fetchLoanStatuses } from '@/lib/api'
import { Book, LoanStatus } from '@/lib/types'
import {
    Heart,
    Loader2,
    BookOpen,
    MapPin,
    Share2,
    ShoppingCart,
    Home,
    ChevronRight,
    User
} from 'lucide-react'
import Link from 'next/link'
import BookCard from '@/components/home/BookCard'
import LibrarySelector from '@/components/LibrarySelector'
import BackButton from '@/components/BackButton'
import { useLibrary } from '@/context/LibraryContext'
import { sendGAEvent } from '@/lib/analytics'
import LoginPromptModal from '@/components/ui/LoginPromptModal'
import ProfileDropdown from '@/components/ProfileDropdown'
import { Button } from '@/components/ui/Button'
import PageHeader from '@/components/PageHeader'
import { getAgeDisplayLabel } from '@/lib/utils/age'
import Image from 'next/image'
import { getOptimizedImageUrl } from '@/lib/utils/image'
import UserAvatar from '@/components/UserAvatar'

interface BookDetailClientProps {
    book: Book
    curationRecommended: Book[]
    ageRecommended: Book[]
}
export default function BookDetailClient({ 
    book: initialBook,
    curationRecommended,
    ageRecommended
}: BookDetailClientProps) {
    const router = useRouter()
    const hasTrackedView = useRef<string | null>(null)
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

    // 태그 리스트 생성 (최대 4개 노출)
    const visibleTags = (() => {
        const tags = []
        if (book.category) {
            tags.push({
                type: 'category',
                text: book.category,
                className: 'bg-blue-50 text-blue-600 border-blue-100'
            })
        }
        if (book.age) {
            tags.push({
                type: 'age',
                text: getAgeDisplayLabel(book.age),
                className: 'bg-amber-50 text-amber-600 border-amber-100'
            })
        }
        if (book.curation_tag) {
            const curationTags = book.curation_tag.split(',')
                .map((tag) => tag.trim())
                .filter(Boolean)
            curationTags.forEach((tag) => {
                tags.push({
                    type: 'curation',
                    text: tag,
                    className: 'bg-brand-primary/5 text-brand-primary border-brand-primary/10'
                })
            })
        }
        return tags.slice(0, 5)
    })()

    // const supabase = createClient()  <-- 제거됨

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
        queryKey: ['book-loan-status', book.id, selectedLibrary],
        queryFn: async () => {
            return await fetchLoanStatuses([book.id], selectedLibrary);
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
            if (status === "시간초과" || status === "확인불가" || status === "확인중") {
                return { ...rawStatus, status: "확인중", available: null };
            }
            if (status === "정보없음" || status === "미소장") {
                return { ...rawStatus, status: "미소장", available: null };
            }
            return rawStatus;
        }

        if (isLoanError) {
            return { status: "확인중", available: null };
        }

        return undefined;
    })();

    // 맥락적 CTA 분기 구조 설계
    const getPurchaseButtonProps = () => {
        // 대출 상태와 관계없이 항상 동일한 문구와 스타일을 반환하여 시각적 깜빡임을 해소합니다.
        return {
            subText: "도서관에 갈 시간이 없다면",
            mainText: "지금 바로 주문하세요",
            variant: "primary" as "primary" | "secondary",
            className: "flex-1 w-full h-14 flex-col gap-0.5 px-2"
        };
    };

    const ctaProps = getPurchaseButtonProps();

    // Send GA event when book detail page is viewed (waits for loan status to resolve to send accurate data)
    useEffect(() => {
        if (normalizedStatus === undefined) return;
        
        const trackKey = `${book.id}_${normalizedStatus.status}`;
        if (hasTrackedView.current === trackKey) return;

        sendGAEvent('view_book_detail', {
            book_id: book.id,
            book_title: book.title,
            call_number: displayCallNo,
            category: book.category,
            age: book.age,
            loan_status: normalizedStatus.status,
            loan_available: normalizedStatus.available
        });
        hasTrackedView.current = trackKey;
    }, [book.id, normalizedStatus, displayCallNo]);

    // Check if book is saved
    useEffect(() => {
        const checkSaved = async () => {
            if (user) {
                const { data: savedData } = await supabase
                    .from('wishlists')
                    .select('id')
                    .match({ user_id: user.id, book_id: book.id })
                    .maybeSingle()

                if (savedData) setIsSaved(true)
            }
        }
        checkSaved()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user, book.id])

    const [isLoginModalOpen, setIsLoginModalOpen] = useState(false)
    const [loginModalProps, setLoginModalProps] = useState({
        title: "좋은 책, 놓치지 않게!",
        description: "전문가가 엄선한 추천작들을 책장에 담아두세요."
    })

    const handleToggleSave = async () => {
        if (!user) {
            sessionStorage.setItem('returnUrl', window.location.pathname)
            sessionStorage.setItem('pendingAction', `like_book_${book.id}`)
            setLoginModalProps({
                title: "좋은 책, 놓치지 않게!",
                description: "전문가가 엄선한 추천작들을 책장에 담아두세요."
            })
            setIsLoginModalOpen(true)
            return
        }

        if (isToggling) return

        // 낙관적 업데이트: DB 응답 기다리지 않고 즉시 UI 반영
        const prevSaved = isSaved
        const prevCount = saveCount
        const nextSaved = !isSaved
        setIsSaved(nextSaved)
        setSaveCount(prev => isSaved ? Math.max(0, prev - 1) : prev + 1)
        setIsToggling(true)

        try {
            if (prevSaved) {
                await unsaveBook(supabase, user.id, book.id)
            } else {
                await saveBook(supabase, user.id, book.id)
            }
            sendGAEvent('toggle_save_book', {
                book_id: book.id,
                book_title: book.title,
                state: nextSaved ? 'save' : 'unsave'
            })
        } catch (err) {
            // 실패 시 이전 상태로 롤백 (반짝임 최소화: state 직접 복원)
            console.error('Failed to toggle save:', err)
            setIsSaved(prevSaved)
            setSaveCount(prevCount)
        } finally {
            setIsToggling(false)
        }
    }

    // Auto-Action: 로그인/가입 후 방금 페이지로 돌아오면 찜하기 자동 실행
    useEffect(() => {
        if (!user) return

        const pendingAction = sessionStorage.getItem('pendingAction')
        if (pendingAction !== `like_book_${book.id}`) return

        // isSaved는 checkSaved가 비동기로 체크하므로 잠시 대기 후 실행
        const timer = setTimeout(async () => {
            // 이미 찜한 상태면 실행 안 함
            const { data: savedData } = await supabase
                .from('wishlists')
                .select('id')
                .match({ user_id: user.id, book_id: book.id })
                .maybeSingle()

            if (savedData) {
                // 이미 찜되어 있음
                setIsSaved(true)
                sessionStorage.removeItem('pendingAction')
                sessionStorage.removeItem('returnUrl')
                return
            }

            setIsToggling(true)
            try {
                await saveBook(supabase, user.id, book.id)
                setIsSaved(true)
                setSaveCount(prev => prev + 1)
                sessionStorage.removeItem('pendingAction')
                sessionStorage.removeItem('returnUrl')
            } catch (err) {
                console.error('Failed auto save:', err)
            } finally {
                setIsToggling(false)
            }
        }, 600)
        return () => clearTimeout(timer)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user, book.id])

    const handleShare = async () => {
        const shareData = {
            title: book.title,
            text: `${book.title}${book.age ? ` (${book.age} 추천)` : ''} - 책자리에서 발견했어요. 도서관 청구기호도 바로 확인 가능!`,
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
        <main className="min-h-screen bg-white pb-6">
            {/* Top Header */}
            <PageHeader 
                title="도서 정보" 
                backHref="/"
                rightSlot={
                    <div className="flex items-center">
                        {user ? (
                            <button
                                onClick={() => router.push('/my-page')}
                                className="p-2 flex items-center justify-center group -mr-2"
                                aria-label="마이 페이지"
                            >
                                <UserAvatar user={user} size={24} className="text-gray-500" />
                            </button>
                        ) : (
                            <button
                                onClick={() => router.push('/auth/signup')}
                                className="p-2 flex items-center justify-center group -mr-2"
                                aria-label="로그인"
                            >
                                <User className="w-6 h-6 text-gray-500 group-hover:text-gray-900 transition-colors" />
                            </button>
                        )}
                    </div>
                }
            />

            <div className="max-w-4xl mx-auto px-6 pt-8">
                <div className="flex flex-col md:flex-row gap-8 md:items-start max-w-5xl mx-auto">
                    {/* Left: Image Card */}
                    <div className="w-full md:w-[35%] shrink-0 max-w-[320px] mx-auto md:mx-0">
                        <div className="relative aspect-[3/4] bg-gray-50 rounded-[28px] overflow-hidden shadow-sm">
                            {book.image_url && !imageError ? (
                                <Image
                                    src={getOptimizedImageUrl(book.image_url, 'detail')}
                                    alt={`${book.title} 표지`}
                                    fill
                                    priority
                                    sizes="(max-width: 768px) 100vw, 400px"
                                    className="object-cover"
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
                                {visibleTags.map((tag, idx) => (
                                    <span 
                                        key={`${tag.type}-${tag.text}-${idx}`} 
                                        className={`px-2.5 py-0.5 rounded-lg text-[11px] font-bold border ${tag.className}`}
                                    >
                                        {tag.text}
                                    </span>
                                ))}
                            </div>

                            <h1 className="text-xl md:text-2xl font-black text-gray-900 leading-tight mb-2 tracking-tight line-clamp-3">
                                {book.title}
                            </h1>

                            {/* AI Curation Note */}
                            {book.curation_note && (
                                <div className="mt-4 mb-6 p-4 bg-gray-50 rounded-2xl border border-gray-100 relative">
                                    <div className="absolute top-0 right-4 -translate-y-1/2 px-2 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 text-[10px] font-bold rounded-full shadow-sm">
                                        전문 사서의 추천 포인트
                                    </div>
                                    <p className="text-[14.5px] text-gray-700 font-bold leading-relaxed tracking-tight">
                                        “{book.curation_note}”
                                    </p>
                                </div>
                            )}

                            <div className="flex flex-col gap-0.5 text-gray-600 font-medium text-base mb-8">
                                <span>{book.author || '정보 없음'}</span>
                                <span className="text-gray-400 text-sm">{book.publisher || '정보 없음'}</span>
                            </div>

                            {user ? (
                                <div className="mb-4">
                                    <div className="mb-2 flex items-center">
                                        <LibrarySelector />
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className={`font-black text-2xl tracking-tight ${displayCallNo === '보유 정보 없음' ? 'text-gray-400' : 'text-gray-900'}`}>
                                            {displayCallNo}{book.vol ? `-${book.vol}` : ''}
                                        </span>
                                        {normalizedStatus && normalizedStatus.status !== "확인중" && (
                                            <span className={`px-2 py-1 rounded-full text-[11px] font-bold leading-none text-center ${normalizedStatus.available === true
                                                ? "bg-green-100 text-green-700"
                                                : normalizedStatus.available === false
                                                    ? "bg-red-100 text-red-700"
                                                    : normalizedStatus.status === "미소장"
                                                        ? "bg-gray-100 text-gray-700"
                                                            : "bg-white text-gray-600 border border-gray-300"
                                                }`}>
                                                {normalizedStatus.status}
                                            </span>
                                        )}
                                    </div>
                                    <button
                                        onClick={() => {
                                            sendGAEvent('click_report_error', { book_id: book.id });
                                            window.open('https://docs.google.com/forms/d/e/1FAIpQLSflKo4QGT_7DUZiwq-w_5lo2ubEDQtJqVsGeX2fsp5P778vhQ/viewform?usp=dialog', '_blank');
                                        }}
                                        className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-gray-400 active:bg-gray-50 active:text-gray-600 border border-gray-200 rounded-lg text-[11px] font-medium mt-3 transition-colors"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m16 2 2 2-7 7H9v-2l7-7Z"/><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 1 1-7.6-11.7 8.38 8.38 0 0 1 3.8.9"/><path d="M12 22v-4"/></svg>
                                        정보가 다른가요? 제보하기
                                    </button>
                                </div>
                            ) : (
                                <div className="mt-2 mb-6 py-1">
                                    <button
                                        onClick={() => {
                                            setLoginModalProps({
                                                title: "좋은 책, 놓치지 않게!",
                                                description: "자주 가는 도서관을 등록하고 실시간 대출 상태와 청구기호를 바로 확인해보세요."
                                            });
                                            setIsLoginModalOpen(true);
                                        }}
                                        className="text-sm sm:text-base font-semibold text-gray-700 active:text-gray-900 transition-colors underline underline-offset-2 py-2 px-1"
                                    >
                                        내 도서관 대출 정보 확인
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Save & Share Area */}
                        <div className="mt-2 pt-6 border-t border-gray-100 flex gap-3 items-end">
                            <div className="relative z-20">
                                {!user?.id && (
                                    <div className="absolute -top-12 left-0 z-50 whitespace-nowrap bg-gray-100 text-gray-700 text-[11px] font-bold px-2.5 py-1.5 rounded-lg pointer-events-none">
                                        찜하고 나중에 확인!
                                        {/* Tooltip Triangle - Pointing to the center of the W-14 button */}
                                        <div className="absolute -bottom-1 left-7 -translate-x-1/2 w-2.5 h-2.5 bg-gray-100 rotate-45"></div>
                                    </div>
                                )}
                                <button
                                    onClick={handleToggleSave}
                                    disabled={isToggling}
                                    className={`w-14 h-14 rounded-lg flex items-center justify-center transition-all transform active:scale-[0.98] border disabled:opacity-60 disabled:cursor-not-allowed ${isSaved
                                        ? "bg-brand-primary/5 text-brand-primary border-brand-primary/30"
                                        : "bg-white text-gray-600 border-gray-200"
                                        }`}
                                    title={isSaved ? "찜 취소" : "찜하기"}
                                >
                                    <Heart className={`w-6 h-6 transition-all ${isSaved ? "fill-current" : ""}`} />
                                </button>
                            </div>
                            <button
                                onClick={handleShare}
                                className="w-14 h-14 flex items-center justify-center bg-white text-gray-600 rounded-lg transition-colors border border-gray-200 active:scale-[0.98] transform"
                                title="공유하기"
                            >
                                <Share2 className="w-6 h-6" />
                            </button>
                            <Button
                                variant={ctaProps.variant}
                                size="lg"
                                onClick={handleBuyKyobo}
                                className={ctaProps.className}
                            >
                                <span className={`text-[10px] font-medium leading-none ${ctaProps.variant === 'primary' ? 'text-white/80' : 'text-gray-400'}`}>
                                    {ctaProps.subText}
                                </span>
                                <div className={`flex items-center font-bold text-sm leading-none ${ctaProps.variant === 'primary' ? 'text-white' : 'text-gray-700'}`}>
                                    <ShoppingCart className="w-4 h-4 mr-1.5 shrink-0" />
                                    <span className="truncate">{ctaProps.mainText}</span>
                                </div>
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Book Description Section */}
            <div className="mt-12 max-w-4xl mx-auto px-6">
                <h3 className="text-lg font-black text-gray-900 mb-4 flex items-center gap-2">
                    도서 소개
                </h3>
                <div className="text-gray-600 leading-relaxed text-sm md:text-base font-medium">
                    {book.description ? (
                        <div
                            dangerouslySetInnerHTML={{ __html: book.description }}
                            className="prose prose-sm max-w-none prose-p:mb-3 prose-strong:text-brand-primary"
                        />
                    ) : (
                        <p className="text-gray-400 italic">등록된 도서 소개 정보가 없습니다.</p>
                    )}
                </div>


            </div>

            {/* Recommendations Section B: Age Group Popular (bg-muted-bg) */}
            {ageRecommended && ageRecommended.length > 0 && (
                <div className="bg-muted-bg pt-8 pb-10 mt-12 w-full px-6">
                    <div className="max-w-4xl mx-auto">
                        <div className="flex items-end justify-between mb-6 px-2">
                            <div className="flex flex-col gap-0.5">
                                <span className="text-[12px] font-bold text-gray-500 tracking-tight">
                                    또래 아이들이 많이 보는
                                </span>
                                <h3 className="text-lg sm:text-xl font-black text-gray-900 tracking-tight leading-tight">
                                    {getAgeDisplayLabel(book.age)} 책 추천 리스트
                                </h3>
                            </div>
                            <Link 
                                href={`/books?age=${encodeURIComponent(book.age || '')}`} 
                                className="text-gray-950 p-1 mb-0.5"
                                aria-label="더보기"
                            >
                                <ChevronRight className="w-6 h-6" />
                            </Link>
                        </div>
                        <div className="overflow-x-auto scrollbar-hide -mx-6 px-6">
                            <div className="flex gap-4 pb-2">
                                {ageRecommended.map((b) => (
                                    <div key={`age-rec-${b.id}`} className="flex-shrink-0 w-[165px] sm:w-[190px]">
                                        <BookCard book={b} />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Recommendations Section A: Same Curation Tag (bg-white) */}
            {curationRecommended && curationRecommended.length > 0 && (
                <div className="bg-white pt-8 pb-2 w-full px-6">
                    <div className="max-w-4xl mx-auto">
                        <div className="flex items-end justify-between mb-6 px-2">
                            <div className="flex flex-col gap-0.5">
                                <span className="text-[12px] font-bold text-gray-500 tracking-tight">
                                    이 책과 함께 읽으면 좋은
                                </span>
                                <h3 className="text-lg sm:text-xl font-black text-gray-900 tracking-tight leading-tight">
                                    {book.curation_tag?.split(',')[0]?.trim() || '추천'} 책 추천 리스트
                                </h3>
                            </div>
                            <Link 
                                href={`/books?curation=${encodeURIComponent(book.curation_tag?.split(',')[0]?.trim() || '')}`} 
                                className="text-gray-950 p-1 mb-0.5"
                                aria-label="더보기"
                            >
                                <ChevronRight className="w-6 h-6" />
                            </Link>
                        </div>
                        <div className="overflow-x-auto scrollbar-hide -mx-6 px-6">
                            <div className="flex gap-4 pb-2">
                                {curationRecommended.map((b) => (
                                    <div key={`curation-rec-${b.id}`} className="flex-shrink-0 w-[165px] sm:w-[190px]">
                                        <BookCard book={b} />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <LoginPromptModal
                isOpen={isLoginModalOpen}
                onClose={() => setIsLoginModalOpen(false)}
                title={loginModalProps.title}
                description={loginModalProps.description}
            />
        </main >
    )
}
