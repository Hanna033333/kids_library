'use client'

import { useState, useEffect, useMemo } from 'react'
import { useQuery, useQueryClient, keepPreviousData } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import { supabase } from '@/lib/supabase'
import { getSavedBooks, unsaveBook } from '@/lib/supabase-api'
import { fetchLoanStatuses } from '@/lib/api'
import { useLibrary } from '@/context/LibraryContext'
import LibrarySelector from '@/components/LibrarySelector'
import { Book, LoanStatus } from '@/lib/types'
import BookItem from '@/components/BookItem'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ProfileDropdown from '@/components/ProfileDropdown'
import PageHeader from '@/components/PageHeader'
import { PageLoader } from '@/components/ui/PageLoader'
import { Share2 } from 'lucide-react'
import LoginPromptModal from '@/components/ui/LoginPromptModal'
import Toast from '@/components/ui/Toast'
import { sendGAEvent } from '@/lib/analytics'

export default function MyLibraryPage() {
    const { user, isLoading: authLoading } = useAuth()
    const { selectedLibrary, selectedLibraryCode } = useLibrary()
    const router = useRouter()
    const queryClient = useQueryClient()

    const [showLoginModal, setShowLoginModal] = useState(false)
    const [toastMessage, setToastMessage] = useState('')
    const [isToastVisible, setIsToastVisible] = useState(false)

    // 비로그인 시 로그인 팝업 오픈
    useEffect(() => {
        if (!authLoading && !user?.id) {
            setShowLoginModal(true)
        } else if (user?.id) {
            setShowLoginModal(false)
        }
    }, [user?.id, authLoading])

    // 저장한 책 목록 (wishlists + childbook_items + book_library_info 단일 쿼리 + React Query 캐시)
    const {
        data: baseSavedBooks = [],
        isLoading: isSavedLoading,
    } = useQuery<Book[]>({
        queryKey: ['saved-books', user?.id],
        queryFn: () => getSavedBooks(supabase, user!.id),
        enabled: !!user?.id,
        staleTime: 2 * 60 * 1000,
        gcTime: 10 * 60 * 1000,
    })

    // 전국 도서관 On-Demand 지원: 저장된 모든 도서에 대해 실시간 대출 상태 조회
    const savedBookIds = useMemo(() => {
        if (!selectedLibrary || baseSavedBooks.length === 0) return []
        return baseSavedBooks.map((book) => book.id)
    }, [baseSavedBooks, selectedLibrary])

    const savedBookIdsKey = savedBookIds.join(',')

    // 실시간 대출 상태 (도서 목록 렌더링을 블로킹하지 않고 비동기 병렬 조회)
    const { data: loanStatuses = {} } = useQuery<Record<number, LoanStatus>>({
        queryKey: ['batch-loan-status', savedBookIdsKey, selectedLibrary, selectedLibraryCode],
        queryFn: () =>
            fetchLoanStatuses(savedBookIds, selectedLibrary!, {
                libCode: selectedLibraryCode,
            }),
        enabled: !!user?.id && !!selectedLibrary && savedBookIds.length > 0,
        staleTime: 5 * 60 * 1000,
        retry: 1,
        placeholderData: keepPreviousData,
    })

    const savedBooks = useMemo<Book[]>(() => {
        if (!selectedLibrary) return baseSavedBooks
        return baseSavedBooks.map((book) => ({
            ...book,
            loan_status: loanStatuses[book.id] || null,
        }))
    }, [baseSavedBooks, loanStatuses, selectedLibrary])

    const availableCount = useMemo(() => {
        return savedBooks.filter(b => b.loan_status?.available === true).length
    }, [savedBooks])

    const handleToggleSaveInCart = async (book: Book, e: React.MouseEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (!user?.id) return

        const queryKey = ['saved-books', user.id]
        const prevBooks = queryClient.getQueryData<Book[]>(queryKey) || baseSavedBooks
        queryClient.setQueryData<Book[]>(
            queryKey,
            prevBooks.filter(item => item.id !== book.id)
        )
        queryClient.setQueryData<number[]>(
            ['saved-book-ids', user.id],
            (old = []) => old.filter(id => id !== book.id)
        )
        try {
            await unsaveBook(supabase, user.id, book.id)
            queryClient.invalidateQueries({ queryKey: ['saved-books', user.id] })
            queryClient.invalidateQueries({ queryKey: ['saved-book-ids', user.id] })
            sendGAEvent('toggle_save_book', {
                book_id: book.id,
                book_title: book.title,
                state: 'unsave',
                source: 'my_library'
            })
        } catch (err) {
            console.error('찜 해제 실패:', err)
            queryClient.setQueryData<Book[]>(queryKey, prevBooks)
            queryClient.invalidateQueries({ queryKey: ['saved-book-ids', user.id] })
        }
    }

    const handleShareLoanList = async () => {
        if (savedBooks.length === 0) return

        const lines = savedBooks.map((b, idx) => {
            const info = selectedLibrary
                ? b.library_info?.find(
                    l => l.library_name === selectedLibrary || l.library_name.includes(selectedLibrary)
                )
                : null
            const resolvedCallno = (info?.callno && info.callno !== '없음')
                ? info.callno
                : (b.loan_status?.callno && b.loan_status.callno !== '없음' ? b.loan_status.callno : null)
            const statusText = b.loan_status?.status || ''
            const callno = resolvedCallno
                ? resolvedCallno
                : (statusText === '대출가능' || statusText === '대출중' ? '청구기호 미제공' : '미소장')
            const status = statusText ? ` (${statusText})` : ''
            return `${idx + 1}. ${b.title} - ${callno}${status}`
        })

        const header = selectedLibrary
            ? `[책자리] ${selectedLibrary} 도서 목록 (${savedBooks.length}권)`
            : `[책자리] 내가 담아둔 책 목록 (${savedBooks.length}권)`
        const shareText = `${header}\n\n${lines.join('\n')}\n\nhttps://checkjari.com/my-library`

        try {
            if (typeof navigator.share === 'function') {
                await navigator.share({
                    title: header,
                    text: shareText,
                })
            } else {
                await navigator.clipboard.writeText(shareText)
                setToastMessage('도서 목록이 복사되었어요! 원하는 곳에 붙여넣어 보세요.')
                setIsToastVisible(true)
            }
            sendGAEvent('share_loan_list', {
                book_count: savedBooks.length,
                library: selectedLibrary || 'none'
            })
        } catch (err) {
            console.error('대출 리스트 공유 실패:', err)
        }
    }

    const isInitialLoading = authLoading || (!!user && isSavedLoading && savedBooks.length === 0)
    if (isInitialLoading) return <PageLoader />

    return (
        <main className="min-h-screen bg-[#F7F7F7] relative">
            <div className={showLoginModal ? 'filter blur-[3px] pointer-events-none select-none transition-all duration-300' : ''}>
                <PageHeader title="내 책장" showHome={true} rightSlot={<ProfileDropdown />} />

                <div className="max-w-7xl mx-auto px-6 py-6">
                    <div className="mb-6 flex flex-col gap-3 border-b border-gray-100 pb-4">
                        <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2 flex-wrap">
                                <p className="text-gray-700 font-bold text-sm sm:text-base">총 {savedBooks.length}권</p>
                                {selectedLibrary && availableCount > 0 && (
                                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-[#ECFDF5] text-[#059669] border border-emerald-200">
                                        대출 가능 {availableCount}권
                                    </span>
                                )}
                            </div>
                            <LibrarySelector />
                        </div>
                    </div>

                    {savedBooks.length === 0 ? (
                        <div className="py-20 flex flex-col items-center justify-center text-center">
                            <p className="text-gray-600 font-bold text-lg mb-1">아직 책장에 꽂아둔 책이 없어요</p>
                            <p className="text-gray-400 text-sm mb-6">도서관 가기 전에 마음에 드는 책을 담아 청구기호를 한눈에 확인해보세요</p>
                            <Link
                                href="/"
                                className="px-6 py-3 bg-brand-primary text-white rounded-lg font-semibold transition-all"
                            >
                                책 보러 가기
                            </Link>
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                            {savedBooks.map((book, idx) => (
                                <BookItem
                                    key={book.id}
                                    book={book}
                                    loanStatus={book.loan_status ?? undefined}
                                    showLibraryInfo={true}
                                    priority={idx < 4}
                                    isSaved={true}
                                    onToggleSave={handleToggleSaveInCart}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* 비로그인 유저 대상 로그인 팝업 모달 */}
            <LoginPromptModal
                isOpen={showLoginModal}
                onClose={() => router.push('/')}
            />

            {/* 우측 하단 플로팅 공유 버튼 (FAB) */}
            {savedBooks.length > 0 && !showLoginModal && (
                <button
                    type="button"
                    onClick={handleShareLoanList}
                    className="fixed bottom-6 right-6 z-40 bg-brand-primary text-white text-xs sm:text-sm font-bold px-4 py-3 rounded-full shadow-[0_4px_16px_rgba(245,158,11,0.35)] hover:bg-brand-primary-dark active:scale-95 transition-all flex items-center gap-2 outline-none focus:outline-none"
                    aria-label="내 책장 목록 공유"
                >
                    <Share2 className="w-4 h-4 text-white" />
                    <span>목록 공유</span>
                </button>
            )}

            <Toast
                message={toastMessage}
                isVisible={isToastVisible}
                onClose={() => setIsToastVisible(false)}
            />
        </main>
    )
}
