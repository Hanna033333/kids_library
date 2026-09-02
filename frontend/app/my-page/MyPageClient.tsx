'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { ChevronRight, Check, Pencil, BookOpen } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'
import LibrarySelector from '@/components/LibrarySelector'
import PageHeader from '@/components/PageHeader'
import { useAuth } from '@/context/AuthContext'
import { supabase } from '@/lib/supabase'
import { getSavedBookIds } from '@/lib/supabase-api'
import { getBooksByIds } from '@/lib/api'
import { Book } from '@/lib/types'
import { getOptimizedImageUrl } from '@/lib/utils/image'
import ConfirmModal from '@/components/ui/ConfirmModal'
import { PageLoader } from '@/components/ui/PageLoader'
import { sendGAEvent } from '@/lib/analytics'
import Toast from '@/components/ui/Toast'

type ViewState = 'main' | 'delete-notice' | 'delete-reason'

/** 내 책장 미리보기 - 이미지별 onError 상태를 독립적으로 관리하는 서브컴포넌트 */
function BookCoverMini({ book }: { book: Book }) {
    const [imgError, setImgError] = useState(false)
    const src = getOptimizedImageUrl(book.image_url, 'list')
    return (
        <div className="relative w-[72px] aspect-[1/1.3] rounded-lg overflow-hidden bg-gray-100 shrink-0">
            {src && !imgError ? (
                <Image
                    src={src}
                    alt={book.title}
                    fill
                    className="object-cover"
                    sizes="72px"
                    onError={() => setImgError(true)}
                />
            ) : (
                <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                    <BookOpen className="w-5 h-5 opacity-20 text-gray-400" />
                </div>
            )}
        </div>
    )
}

const ADJECTIVES = ['지혜로운', '따스한', '포근한', '정겨운', '행복한', '다정한', '꿈꾸는', '다독이는', '슬기로운', '다복한', '마음넓은', '빛나는']
const NOUNS = ['책벌레', '이야기꾼', '책부엉이', '파랑새', '독서가', '책요정', '글벗', '책탐험가', '책마을님']

function generateRandomNickname() {
    const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]
    const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)]
    return `${adj}${noun}`
}

const DELETE_REASONS = [
    '자주 사용하지 않아서',
    '도서 정보 / 청구기호가 부족해서',
    '잦은 시스템 오류 때문에',
    '전반적으로 이용이 어려워서',
    '개인정보 및 보안 우려 때문에',
    '다른 아이디로 가입하고자',
    '기타(직접 작성)',
]

export default function MyPageClient() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const isAutoOpenLibrary = searchParams?.get('action') === 'select-library'
    const { user, isLoading: authLoading, signOut } = useAuth()

    const [currentView, setCurrentView] = useState<ViewState>('main')

    // 회원탈퇴 STEP 1
    const [deleteAgreed, setDeleteAgreed] = useState(false)
    const [wishlistCount, setWishlistCount] = useState<number | null>(null)

    // 회원탈퇴 STEP 2
    const [deleteReason, setDeleteReason] = useState('')
    const [deleteReasonText, setDeleteReasonText] = useState('')
    const [isDeleting, setIsDeleting] = useState(false)

    // 내 책장 미리보기
    const [previewBooks, setPreviewBooks] = useState<Book[]>([])
    const [savedCount, setSavedCount] = useState<number>(0)
    const [isPreviewLoading, setIsPreviewLoading] = useState(true)

    // 닉네임
    const [nickname, setNickname] = useState<string | null>(null)
    const [editNickname, setEditNickname] = useState('')
    const [isSavingNickname, setIsSavingNickname] = useState(false)
    const [isNicknameModalOpen, setIsNicknameModalOpen] = useState(false)

    // 오류 모달
    const [errorMessage, setErrorMessage] = useState('')
    const [isErrorModalOpen, setIsErrorModalOpen] = useState(false)

    // 토스트
    const [toastMessage, setToastMessage] = useState('')

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/')
        }
    }, [user, authLoading, router])

    useEffect(() => {
        // Supabase 토큰 갱신 교착 등으로 쿼리가 응답/에러 없이 hang되면 스켈레톤이 영구 노출되므로
        // 각 비동기 호출에 타임아웃을 걸어 반드시 결말이 나도록 보장한다.
        const withTimeout = <T,>(p: Promise<T>, ms: number, fallback: T): Promise<T> =>
            Promise.race([p, new Promise<T>((resolve) => setTimeout(() => resolve(fallback), ms))])

        const fetchPreview = async () => {
            if (!user) return
            setIsPreviewLoading(true)
            try {
                const savedIds = await withTimeout(getSavedBookIds(supabase, user.id), 6000, [] as number[])
                setSavedCount(savedIds.length)
                if (savedIds.length > 0) {
                    const books = await withTimeout(getBooksByIds(savedIds.slice(0, 6)), 6000, [] as Book[])
                    setPreviewBooks(books)
                }
            } catch (err) {
                console.error('내 책장 미리보기 로드 실패:', err)
            } finally {
                // 취소 여부와 무관하게 무조건 해제 (조건부 해제 시 스켈레톤 stuck 재발)
                setIsPreviewLoading(false)
            }
        }
        if (user) fetchPreview()
    }, [user])

    useEffect(() => {
        const fetchSettings = async () => {
            if (!user) return
            const isQaMode = typeof window !== 'undefined' && (
                sessionStorage.getItem('qa_mode') === 'true' ||
                localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN'
            )
            if (isQaMode) {
                // QA 모드: sessionStorage에 저장된 닉네임 복원 (SignupWelcomeModal 또는 이전 저장값)
                let qaNickname = sessionStorage.getItem('qa_saved_nickname') || null
                if (!qaNickname) {
                    qaNickname = generateRandomNickname()
                    sessionStorage.setItem('qa_saved_nickname', qaNickname)
                }
                setNickname(qaNickname)
                setEditNickname(qaNickname)
                return
            }

            const { data, error } = await supabase
                .from('members')
                .select('nickname')
                .eq('id', user.id)
                .single()
            if (data && !error) {
                const saved = data.nickname || null
                if (saved) {
                    setNickname(saved)
                    setEditNickname(saved)
                } else {
                    // 닉네임 미설정 시 랜덤 닉네임 자동 부여
                    const autoNickname = generateRandomNickname()
                    setNickname(autoNickname)
                    setEditNickname(autoNickname)
                    try {
                        const isLocal = typeof window !== 'undefined' && (
                            window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                        )
                        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (isLocal ? 'http://127.0.0.1:8000' : 'https://api.checkjari.com')
                        const { data: sessionData } = await supabase.auth.getSession()
                        const token = sessionData?.session?.access_token || ''
                        await fetch(`${API_BASE_URL}/api/auth/me`, {
                            method: 'PATCH',
                            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                            body: JSON.stringify({ nickname: autoNickname }),
                        })
                    } catch {
                        // 자동 저장 실패는 조용히 무시 — 유저가 수동으로 수정 가능
                    }
                }
            }
        }
        fetchSettings()
    }, [user])

    if (authLoading || !user) {
        return <PageLoader />
    }

    const handleSignOut = async () => {
        if (typeof window !== 'undefined') {
            sessionStorage.setItem('showLogoutToast', 'true')
        }
        sendGAEvent('logout')
        await signOut()
        router.push('/')
    }

    const handleDeleteAccount = async () => {
        if (!deleteReason || isDeleting) return
        setIsDeleting(true)
        try {
            const isQaMode = typeof window !== 'undefined' && (
                sessionStorage.getItem('qa_mode') === 'true' ||
                localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN'
            )
            let token = ''
            if (isQaMode) {
                token = 'TEST_QA_TOKEN'
            } else {
                const { data: sessionData } = await supabase.auth.getSession()
                token = sessionData?.session?.access_token || ''
            }
            if (!token) throw new Error('세션을 찾을 수 없습니다.')

            const isLocal = typeof window !== 'undefined' && (
                window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            )
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (isLocal ? 'http://127.0.0.1:8000' : 'https://api.checkjari.com')
            const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` },
            })

            if (!res.ok) {
                setErrorMessage('회원 탈퇴 처리 중 오류가 발생했습니다. 고객센터로 문의해주세요.')
                setIsErrorModalOpen(true)
            } else {
                if (typeof window !== 'undefined') {
                    sessionStorage.setItem('showWithdrawnPopup', 'true')
                }
                sendGAEvent('delete_account', {
                    method: 'oauth',
                    reason: deleteReason,
                    reason_detail: deleteReason === '기타(직접 작성)' ? deleteReasonText : ''
                })
                await signOut()
                router.push('/')
            }
        } catch (err: any) {
            console.error('Account deletion error:', err)
            setErrorMessage('회원 탈퇴 중 오류가 발생했습니다.')
            setIsErrorModalOpen(true)
        } finally {
            setIsDeleting(false)
        }
    }

    const fetchWishlistCount = async () => {
        if (!user) return
        const { count } = await supabase
            .from('wishlists')
            .select('*', { count: 'exact', head: true })
            .eq('user_id', user.id)
        setWishlistCount(count ?? 0)
    }

    const resetDelete = () => {
        setDeleteAgreed(false)
        setDeleteReason('')
        setDeleteReasonText('')
    }

    // 닉네임 유효성
    const nicknameValidation = (() => {
        const trimmed = editNickname.trim()
        return {
            isLengthValid: trimmed.length >= 2 && trimmed.length <= 10,
            isFormatValid: trimmed.length === 0 || /^[가-힣a-zA-Z0-9]+$/.test(trimmed),
        }
    })()
    const isNicknameValid = nicknameValidation.isLengthValid && nicknameValidation.isFormatValid
    const isNicknameChanged = editNickname.trim() !== (nickname ?? '')

    const handleSaveNickname = async () => {
        if (!isNicknameValid || isSavingNickname) return
        setIsSavingNickname(true)
        try {
            const isQaMode = typeof window !== 'undefined' && (
                sessionStorage.getItem('qa_mode') === 'true' ||
                localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN'
            )

            if (isQaMode) {
                // QA 모드: 실제 API 호출 없이 sessionStorage에만 저장
                sessionStorage.setItem('qa_saved_nickname', editNickname.trim())
            } else {
                const isLocal = typeof window !== 'undefined' && (
                    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                )
                const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (isLocal ? 'http://127.0.0.1:8000' : 'https://api.checkjari.com')
                const { data: sessionData } = await supabase.auth.getSession()
                const token = sessionData?.session?.access_token || ''

                const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                    body: JSON.stringify({ nickname: editNickname.trim() }),
                })
                if (!res.ok) throw new Error('Failed')
            }

            setNickname(editNickname.trim())
            setIsNicknameModalOpen(false)
            setToastMessage('닉네임이 변경되었어요')
        } catch {
            setErrorMessage('닉네임 저장 중 오류가 발생했습니다.')
            setIsErrorModalOpen(true)
        } finally {
            setIsSavingNickname(false)
        }
    }

    const getTitle = () => {
        if (currentView.startsWith('delete')) return '회원 탈퇴'
        return '마이 페이지'
    }

    const getBackHandler = () => {
        if (currentView === 'main') return undefined
        if (currentView === 'delete-notice') return () => { resetDelete(); setCurrentView('main') }
        if (currentView === 'delete-reason') return () => setCurrentView('delete-notice')
        return undefined
    }

    return (
        <main className="min-h-screen bg-[#F5F5F8]">
            <div className="w-full min-h-screen flex flex-col">
                <PageHeader
                    title={getTitle()}
                    backOnClick={getBackHandler()}
                />
                <div className="flex-1 w-full max-w-2xl mx-auto p-4 sm:p-6 pb-12 space-y-4">

                    {/* ===== MAIN ===== */}
                    {currentView === 'main' && (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-300 space-y-4">

                            {/* 프로필 카드 */}
                            <div className="p-5 bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] flex items-center gap-4">
                                <div className="w-14 h-14 bg-[#FDF6E3] rounded-full flex items-center justify-center text-[#F59E0B] text-xl font-bold shrink-0">
                                    {(nickname?.[0] ?? user.email?.[0] ?? '?').toUpperCase()}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-baseline gap-1.5">
                                        <p className="text-base font-bold text-gray-900 truncate">
                                            {nickname || <span className="text-gray-400 font-medium">닉네임을 설정해주세요</span>}
                                        </p>
                                        <button
                                            onClick={() => { setEditNickname(nickname || editNickname); setIsNicknameModalOpen(true) }}
                                            className="text-gray-400 active:text-gray-600 transition-colors shrink-0"
                                            aria-label="닉네임 수정"
                                        >
                                            <Pencil className="w-[13px] h-[13px]" />
                                        </button>
                                    </div>
                                    <p className="text-[13px] text-gray-400 truncate mt-0.5">{user.email}</p>
                                </div>
                            </div>

                            {/* 내 도서관 */}
                            <div className="bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] overflow-hidden">
                                <div className="w-full flex items-center justify-between px-5 py-4 gap-3 min-w-0">
                                    <span className="font-bold text-gray-900 text-[15px] shrink-0 whitespace-nowrap">내 도서관</span>
                                    <div className="min-w-0 shrink flex justify-end">
                                        <LibrarySelector autoOpen={isAutoOpenLibrary} />
                                    </div>
                                </div>
                            </div>

                            {/* 내 책장 미리보기 섹션 */}
                            <div className="bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-5">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-gray-900 text-[15px]">내 책장</span>
                                        {savedCount > 0 && (
                                            <span className="text-[13px] text-gray-400 font-medium">저장 {savedCount}권</span>
                                        )}
                                    </div>
                                    <Link
                                        href="/my-library"
                                        className="flex items-center gap-0.5 text-[13px] text-gray-400 active:text-gray-600 transition-colors"
                                    >
                                        <ChevronRight className="w-4 h-4" />
                                    </Link>
                                </div>

                                {isPreviewLoading ? (
                                    <div className="flex gap-3">
                                        {[...Array(4)].map((_, i) => (
                                            <div key={i} className="w-[72px] shrink-0 aspect-[1/1.3] bg-gray-100 rounded-lg animate-pulse" />
                                        ))}
                                    </div>
                                ) : previewBooks.length === 0 ? (
                                    <div className="py-5 text-center">
                                        <p className="text-[13px] text-gray-400 mb-3">아직 담아둔 책이 없어요</p>
                                        <Link
                                            href="/"
                                            className="inline-block px-5 py-2.5 bg-gray-100 text-gray-600 text-[13px] font-semibold rounded-xl active:bg-gray-200 transition-colors"
                                        >
                                            책 둘러보기
                                        </Link>
                                    </div>
                                ) : (
                                    <div className="flex gap-3 overflow-x-auto scrollbar-hide -mx-5 px-5">
                                        {previewBooks.map((book) => (
                                            <Link key={book.id} href={`/book/${book.id}`} className="shrink-0">
                                                <BookCoverMini book={book} />
                                            </Link>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* 로그아웃 + 회원 탈퇴 — 한 줄 텍스트 */}
                            <div className="flex items-center justify-between px-1 pt-1">
                                <button
                                    onClick={() => { setCurrentView('delete-notice'); fetchWishlistCount() }}
                                    className="text-[13px] font-medium text-gray-400 active:text-gray-600 transition-colors py-2 px-1"
                                >
                                    회원 탈퇴
                                </button>
                                <button
                                    onClick={handleSignOut}
                                    className="text-[13px] font-medium text-gray-500 active:text-gray-800 transition-colors py-2 px-1"
                                >
                                    로그아웃
                                </button>
                            </div>
                        </div>
                    )}

                    {/* ===== DELETE STEP 1: 유의사항 확인 ===== */}
                    {currentView === 'delete-notice' && (
                        <div className="animate-in fade-in slide-in-from-right-4 duration-300 bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-6">
                            <div className="py-4 border-b border-gray-100 mb-6">
                                <p className="text-[13px] font-bold text-gray-800 mb-3">{nickname || user.email?.split('@')[0]}의 책자리</p>
                                <div className="flex items-center justify-between py-2 border-t border-gray-100">
                                    <span className="text-[13px] text-gray-600">찜한 도서</span>
                                    <span className="text-[13px] font-semibold text-gray-900">
                                        {wishlistCount === null ? '...' : `${wishlistCount}권`}
                                    </span>
                                </div>
                            </div>

                            <h2 className="text-[17px] font-bold text-gray-900 mb-4">탈퇴 회원 유의 사항</h2>

                            <ul className="text-[13px] text-gray-600 space-y-3 leading-relaxed mb-8">
                                <li className="flex gap-2">
                                    <span className="text-gray-400 shrink-0">·</span>
                                    <span>탈퇴를 하실 경우 계정과 함께 등록된 찜 목록 및 개인정보가 모두 소멸됩니다. 원치 않으실 경우, 탈퇴를 보류해주시기 바랍니다.</span>
                                </li>
                                <li className="flex gap-2">
                                    <span className="text-gray-400 shrink-0">·</span>
                                    <span>탈퇴 후 동일한 이메일로 재가입 시, 기존 데이터는 복구되지 않습니다.</span>
                                </li>
                            </ul>

                            <label className="flex items-start gap-3 mb-8 cursor-pointer group">
                                <div
                                    className={`w-5 h-5 mt-0.5 rounded border-2 flex items-center justify-center transition-all shrink-0 ${
                                        deleteAgreed ? 'bg-[#F59E0B] border-[#F59E0B]' : 'border-gray-300 group-hover:border-[#F59E0B]'
                                    }`}
                                    onClick={() => setDeleteAgreed(!deleteAgreed)}
                                >
                                    {deleteAgreed && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                                </div>
                                <span className="text-[13px] text-gray-700 leading-relaxed text-left">
                                    회원 탈퇴에 관한 모든 내용을 숙지하였고, 회원 탈퇴를 신청합니다.
                                </span>
                            </label>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => { resetDelete(); setCurrentView('main') }}
                                    className="flex-1 py-3.5 text-gray-600 font-bold bg-gray-100 rounded-lg active:bg-gray-200 transition-colors text-[15px]"
                                >
                                    나중에 하기
                                </button>
                                <button
                                    disabled={!deleteAgreed}
                                    onClick={() => setCurrentView('delete-reason')}
                                    className={`flex-1 py-3.5 font-bold rounded-lg transition-colors text-[15px] ${
                                        deleteAgreed ? 'bg-[#F59E0B] text-white active:bg-[#D97706]' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                    }`}
                                >
                                    계속 진행하기
                                </button>
                            </div>
                        </div>
                    )}

                    {/* ===== DELETE STEP 2: 탈퇴 사유 입력 ===== */}
                    {currentView === 'delete-reason' && (
                        <div className="animate-in fade-in slide-in-from-right-4 duration-300 bg-white rounded-2xl shadow-[0_1px_4px_rgba(0,0,0,0.06)] p-6">
                            <h2 className="text-[17px] font-bold text-gray-900 mb-5">탈퇴 사유 입력</h2>

                            <div className="divide-y divide-gray-100 mb-6">
                                {DELETE_REASONS.map((reason) => (
                                    <label
                                        key={reason}
                                        className="flex items-center gap-3 py-4 cursor-pointer"
                                        onClick={() => setDeleteReason(reason)}
                                    >
                                        <div
                                            className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-all ${
                                                deleteReason === reason ? 'border-[#F59E0B]' : 'border-gray-300'
                                            }`}
                                        >
                                            {deleteReason === reason && (
                                                <div className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]" />
                                            )}
                                        </div>
                                        <span className="text-[15px] text-gray-700">{reason}</span>
                                    </label>
                                ))}
                            </div>

                            {deleteReason === '기타(직접 작성)' && (
                                <textarea
                                    value={deleteReasonText}
                                    onChange={(e) => setDeleteReasonText(e.target.value)}
                                    placeholder="탈퇴 사유를 간략히 입력해주세요"
                                    maxLength={200}
                                    rows={4}
                                    className="w-full mb-6 px-4 py-3 border border-gray-200 rounded-lg text-[14px] text-gray-700 placeholder-gray-400 resize-none focus:outline-none focus:border-[#F59E0B] transition"
                                />
                            )}

                            <div className="flex gap-3">
                                <button
                                    onClick={() => { resetDelete(); setCurrentView('main') }}
                                    className="flex-1 py-3.5 text-gray-600 font-bold bg-gray-100 rounded-lg active:bg-gray-200 transition-colors text-[15px]"
                                >
                                    나중에 하기
                                </button>
                                <button
                                    disabled={!deleteReason || (deleteReason === '기타(직접 작성)' && !deleteReasonText.trim()) || isDeleting}
                                    onClick={handleDeleteAccount}
                                    className={`flex-1 py-3.5 font-bold rounded-lg transition-colors text-[15px] ${
                                        deleteReason && !(deleteReason === '기타(직접 작성)' && !deleteReasonText.trim()) && !isDeleting
                                            ? 'bg-[#F59E0B] text-white active:bg-[#D97706]'
                                            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                    }`}
                                >
                                    {isDeleting ? '처리 중...' : '탈퇴하기'}
                                </button>
                            </div>
                        </div>
                    )}

                </div>

                {/* 닉네임 수정 모달 */}
                {isNicknameModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center px-6 bg-black/50 backdrop-blur-sm">
                        <div className="w-full max-w-[340px] bg-white rounded-[16px] p-6">
                            <h2 className="text-[20px] font-bold text-gray-900 mb-1">닉네임 변경</h2>
                            <p className="text-[14px] text-gray-400 mb-5">2~10자, 한글·영문·숫자만 사용 가능해요</p>
                            <input
                                type="text"
                                value={editNickname}
                                onChange={(e) => setEditNickname(e.target.value.replace(/\s/g, ''))}
                                maxLength={10}
                                autoFocus
                                className="w-full h-12 px-4 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:border-gray-900 focus:bg-white transition-all text-[16px] text-gray-900 mb-2"
                                placeholder="닉네임 입력"
                            />
                            <p className={`text-[12px] px-0.5 mb-5 h-4 leading-4 ${
                                editNickname.length === 0 ? 'text-transparent' :
                                isNicknameValid ? 'text-[#10B981]' : 'text-red-400'
                            }`}>
                                {!nicknameValidation.isFormatValid ? '특수문자나 공백은 사용할 수 없어요' :
                                 !nicknameValidation.isLengthValid ? '2자 이상 10자 이하로 입력해주세요' :
                                 isNicknameChanged ? '사용 가능한 닉네임이에요' : '현재 닉네임이에요'}
                            </p>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setIsNicknameModalOpen(false)}
                                    className="flex-1 h-12 rounded-xl text-[15px] font-bold bg-gray-100 text-gray-600 active:bg-gray-200 transition-colors"
                                >
                                    취소
                                </button>
                                <button
                                    onClick={handleSaveNickname}
                                    disabled={!isNicknameValid || !isNicknameChanged || isSavingNickname}
                                    className={`flex-1 h-12 rounded-xl text-[15px] font-bold transition-all active:scale-[0.98] ${
                                        isNicknameValid && isNicknameChanged && !isSavingNickname
                                            ? 'bg-[#F59E0B] text-white active:bg-[#D97706]'
                                            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                    }`}
                                >
                                    {isSavingNickname ? '저장 중...' : '저장'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* 오류 안내 팝업 */}
                <ConfirmModal
                    isOpen={isErrorModalOpen}
                    onClose={() => setIsErrorModalOpen(false)}
                    onConfirm={() => setIsErrorModalOpen(false)}
                    title="오류 발생"
                    description={errorMessage}
                    confirmLabel="확인"
                    cancelLabel=""
                    confirmVariant="primary"
                />

                {/* 토스트 */}
                <Toast
                    message={toastMessage}
                    isVisible={!!toastMessage}
                    onClose={() => setToastMessage('')}
                />
            </div>
        </main>
    )
}
