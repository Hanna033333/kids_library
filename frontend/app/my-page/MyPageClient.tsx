'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ChevronRight, Lock, Loader2, Check } from 'lucide-react'
import PageHeader from '@/components/PageHeader'
import { useAuth } from '@/context/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import ConfirmModal from '@/components/ui/ConfirmModal'
import { Spinner } from '@/components/ui/Spinner'
import { PageLoader } from '@/components/ui/PageLoader'
import { sendGAEvent } from '@/lib/analytics'
import Toast from '@/components/ui/Toast'

type ViewState = 'main' | 'account' | 'password' | 'delete-notice' | 'delete-reason' | 'delete-password'

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
    const { user, isLoading: authLoading, signOut } = useAuth()

    const [currentView, setCurrentView] = useState<ViewState>('main')

    // 비밀번호 변경
    const [currentPassword, setCurrentPassword] = useState('')
    const [newPassword, setNewPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [isUpdatingPassword, setIsUpdatingPassword] = useState(false)
    const [passwordMessage, setPasswordMessage] = useState({ type: '', text: '' })

    // 회원탈퇴 STEP 1 - 유의사항
    const [deleteAgreed, setDeleteAgreed] = useState(false)
    const [wishlistCount, setWishlistCount] = useState<number | null>(null)

    // 회원탈퇴 STEP 2 - 탈퇴 사유
    const [deleteReason, setDeleteReason] = useState('')
    const [deleteReasonText, setDeleteReasonText] = useState('')

    // 회원탈퇴 STEP 3 - 비밀번호 확인
    const [deletePassword, setDeletePassword] = useState('')
    const [deletePasswordError, setDeletePasswordError] = useState('')
    const [isDeleting, setIsDeleting] = useState(false)

    // 오류 모달
    const [errorMessage, setErrorMessage] = useState('')
    const [isErrorModalOpen, setIsErrorModalOpen] = useState(false)

    // 마케팅 수신 동의
    const [marketingConsent, setMarketingConsent] = useState(false)
    const [isMarketingLoading, setIsMarketingLoading] = useState(false)
    const [isMarketingOffModalOpen, setIsMarketingOffModalOpen] = useState(false)
    const [isMarketingOnNoticeOpen, setIsMarketingOnNoticeOpen] = useState(false)
    const [marketingOffDate, setMarketingOffDate] = useState('')
    const [toastMessage, setToastMessage] = useState('')

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/')
        }
    }, [user, authLoading, router])

    useEffect(() => {
        const fetchSettings = async () => {
            if (user) {
                // QA Mode 방어
                const isQaMode = typeof window !== 'undefined' && (sessionStorage.getItem('qa_mode') === 'true' || localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN')
                if (isQaMode) {
                    setMarketingConsent(false)
                    return
                }

                const { data, error } = await supabase
                    .from('members')
                    .select('agreed_to_marketing')
                    .eq('id', user.id)
                    .single()
                if (data && !error) {
                    setMarketingConsent(data.agreed_to_marketing || false)
                }
            }
        }
        fetchSettings()
    }, [user])

    if (authLoading || !user) {
        return (
            <PageLoader />
        )
    }

    const handleSignOut = async () => {
        if (typeof window !== 'undefined') {
            sessionStorage.setItem('showLogoutToast', 'true')
        }
        sendGAEvent('logout')
        await signOut()
        router.push('/')
    }

    const handleUpdatePassword = async (e: React.FormEvent) => {
        e.preventDefault()
        setPasswordMessage({ type: '', text: '' })

        if (!currentPassword) {
            setPasswordMessage({ type: 'error', text: '현재 비밀번호를 입력해주세요.' })
            return
        }
        if (newPassword.length < 8 || newPassword.length > 20) {
            setPasswordMessage({ type: 'error', text: '비밀번호는 8자 이상 20자 이내여야 합니다.' })
            return
        }
        if (!/[a-zA-Z]/.test(newPassword)) {
            setPasswordMessage({ type: 'error', text: '비밀번호에 영문을 포함해야 합니다.' })
            return
        }
        if (!/\d/.test(newPassword)) {
            setPasswordMessage({ type: 'error', text: '비밀번호에 숫자를 포함해야 합니다.' })
            return
        }
        if (newPassword !== confirmPassword) {
            setPasswordMessage({ type: 'error', text: '비밀번호가 일치하지 않습니다.' })
            return
        }

        setIsUpdatingPassword(true)
        try {
             // QA Mode 통과
            const isQaMode = typeof window !== 'undefined' && (sessionStorage.getItem('qa_mode') === 'true' || localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN')

            if (!isQaMode) {
                // STEP 1: 현재 비밀번호 확인
                const { error: signInError } = await supabase.auth.signInWithPassword({
                    email: user.email!,
                    password: currentPassword,
                })
                if (signInError) {
                    throw new Error('현재 비밀번호가 올바르지 않습니다.')
                }

                // STEP 2: 새 비밀번호로 업데이트
                const { error } = await supabase.auth.updateUser({ password: newPassword })
                if (error) throw error
            }

            setCurrentPassword('')
            setNewPassword('')
            setConfirmPassword('')
            setCurrentView('account')
            setToastMessage('비밀번호가 변경되었습니다.')
        } catch (err: any) {
            console.error('Password update error:', err)
            let errorMsg = err.message || '비밀번호 변경에 실패했습니다.'
            if (errorMsg === 'New password should be different from the old password.') {
                errorMsg = '기존 비밀번호와 다른 비밀번호를 입력해주세요.'
            }
            setPasswordMessage({ type: 'error', text: errorMsg })
        } finally {
            setIsUpdatingPassword(false)
        }
    }

    // 탈퇴 처리 (STEP 3 완료)
    const handleDeleteAccount = async (e: React.FormEvent) => {
        e.preventDefault()
        setDeletePasswordError('')
        if (!deletePassword) return

        setIsDeleting(true)
        try {
            // QA Mode 통과
            const isQaMode = typeof window !== 'undefined' && (sessionStorage.getItem('qa_mode') === 'true' || localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN')
            
            if (!isQaMode) {
                // STEP 1: 비밀번호 재확인
                const { error: signInError } = await supabase.auth.signInWithPassword({
                    email: user.email!,
                    password: deletePassword,
                })
                if (signInError) {
                    setDeletePasswordError('비밀번호가 올바르지 않습니다. 다시 확인해주세요.')
                    setIsDeleting(false)
                    return
                }
            }

            // STEP 2: 세션 토큰 가져와서 백엔드 DELETE 호출
            let token = ''
            if (isQaMode) {
                token = 'TEST_QA_TOKEN'
            } else {
                const { data: sessionData } = await supabase.auth.getSession()
                token = sessionData?.session?.access_token || ''
            }
            if (!token) throw new Error('세션을 찾을 수 없습니다.')

            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
            const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` },
            })

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}))
                console.warn('Delete account API failed:', errData)
                setErrorMessage('회원 탈퇴 처리 중 오류가 발생했습니다. 고객센터로 문의해주세요.')
                setIsErrorModalOpen(true)
            } else {
                if (typeof window !== 'undefined') {
                    sessionStorage.setItem('showWithdrawnPopup', 'true')
                }
                sendGAEvent('delete_account', { 
                    method: 'password',
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

    // 마케팅 수신 동의 토글
    const handleToggleClick = () => {
        if (!marketingConsent) {
            // OFF -> ON 시도: 팝업부터 띄움
            setIsMarketingOnNoticeOpen(true)
        } else {
            // ON -> OFF 시도: 바로 해제 진행
            executeMarketingToggle(false)
        }
    }

    const executeMarketingToggle = async (newValue: boolean) => {
        if (!user || isMarketingLoading) return
        setIsMarketingLoading(true)
        
        // Optimistic update
        setMarketingConsent(newValue)
        
        // QA Mode
        const isQaMode = typeof window !== 'undefined' && (sessionStorage.getItem('qa_mode') === 'true' || localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN')
        if (isQaMode) {
            setIsMarketingLoading(false)
            const today = new Date()
            const dateStr = `${String(today.getFullYear()).slice(2)}/${String(today.getMonth() + 1).padStart(2, '0')}/${String(today.getDate()).padStart(2, '0')}`
            if (!newValue) { // OFF
                setMarketingOffDate(dateStr)
                setIsMarketingOffModalOpen(true)
            } else { // ON
                setIsMarketingOnNoticeOpen(false)
                setToastMessage(`책자리 혜택알림 수신동의 완료 (수신처리일 ${dateStr})`)
            }
            return
        }

        const { error } = await supabase
            .from('members')
            .update({ agreed_to_marketing: newValue })
            .eq('id', user.id)
            
        if (error) {
            // Revert on error
            setMarketingConsent(!newValue)
            setErrorMessage('마케팅 수신 동의 설정 변경 중 오류가 발생했습니다.')
            setIsErrorModalOpen(true)
        } else {
            const today = new Date()
            const dateStr = `${String(today.getFullYear()).slice(2)}/${String(today.getMonth() + 1).padStart(2, '0')}/${String(today.getDate()).padStart(2, '0')}`
            if (!newValue) { // OFF
                setMarketingOffDate(dateStr)
                setIsMarketingOffModalOpen(true)
            } else { // ON
                setIsMarketingOnNoticeOpen(false)
                setToastMessage(`책자리 혜택알림 수신동의 완료 (수신처리일 ${dateStr})`)
                setToastMessage('비밀번호가 변경되었습니다.')
            }
        }
        
        setIsMarketingLoading(false)
    }

    // 찜한 도서 수 조회
    const fetchWishlistCount = async () => {
        if (!user) return
        const { count } = await supabase
            .from('wishlists')
            .select('*', { count: 'exact', head: true })
            .eq('user_id', user.id)
        setWishlistCount(count ?? 0)
    }

    // 탈퇴 state 초기화 (취소/나중에 하기)
    const resetDelete = () => {
        setDeleteAgreed(false)
        setDeleteReason('')
        setDeleteReasonText('')
        setDeletePassword('')
        setDeletePasswordError('')
    }

    const getTitle = () => {
        if (currentView === 'account') return '계정 관리'
        if (currentView === 'password') return '비밀번호 변경'
        if (currentView.startsWith('delete')) return '회원 탈퇴'
        return '마이 페이지'
    }

    const getBackHandler = () => {
        if (currentView === 'main') return undefined
        if (currentView === 'account') return () => setCurrentView('main')
        if (currentView === 'delete-notice') return () => { resetDelete(); setCurrentView('account') }
        if (currentView === 'delete-reason') return () => setCurrentView('delete-notice')
        if (currentView === 'delete-password') return () => setCurrentView('delete-reason')
        // password view
        return () => {
            setCurrentView('account')
            setPasswordMessage({ type: '', text: '' })
            setCurrentPassword('')
            setNewPassword('')
            setConfirmPassword('')
        }
    }

    return (
        <main className="min-h-screen bg-[#F7F7F7]">
            <div className="max-w-lg mx-auto bg-white min-h-screen sm:shadow-sm sm:border-x border-gray-100">
                <PageHeader
                    title={getTitle()}
                    backOnClick={getBackHandler()}
                />
                <div className="pb-12">

                    {/* ===== MAIN ===== */}
                    {currentView === 'main' && (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
                            <button
                                onClick={() => setCurrentView('account')}
                                className="w-full text-left px-6 py-8 border-b-8 border-gray-50 flex items-center gap-4 transition-colors"
                            >
                                <div className="w-16 h-16 bg-[#FDF6E3] rounded-full flex items-center justify-center text-[#F59E0B] text-2xl font-bold shrink-0">
                                    {user.email?.[0].toUpperCase()}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-base font-bold text-gray-900 truncate">{user.email}</p>
                                </div>
                                <ChevronRight className="w-5 h-5 text-gray-400 shrink-0" />
                            </button>

                            <div className="flex flex-col">
                                <div className="py-2 border-b-8 border-gray-50">
                                    <button
                                        onClick={() => router.push('/my-library')}
                                        className="w-full flex items-center justify-between px-6 py-3.5 transition-colors"
                                    >
                                        <span className="font-medium text-gray-900 text-[15px]">내 책장</span>
                                        <ChevronRight className="w-5 h-5 text-gray-400" />
                                    </button>
                                </div>
                                <div className="py-2 border-b-8 border-gray-50 divide-y divide-gray-100">
                                    <Link href="/terms" className="w-full flex items-center justify-between px-6 py-3.5 transition-colors">
                                        <span className="font-medium text-gray-900 text-[15px]">이용약관</span>
                                        <ChevronRight className="w-5 h-5 text-gray-400" />
                                    </Link>
                                    <Link href="/privacy" className="w-full flex items-center justify-between px-6 py-3.5 transition-colors">
                                        <span className="font-medium text-gray-900 text-[15px]">개인정보보호정책</span>
                                        <ChevronRight className="w-5 h-5 text-gray-400" />
                                    </Link>
                                    <a 
                                        href="mailto:contact@chaekjari.com" 
                                        className="w-full flex items-center justify-between px-6 py-3.5 transition-colors"
                                        onClick={() => sendGAEvent('click_customer_inquiry')}
                                    >
                                        <span className="font-medium text-gray-900 text-[15px]">고객문의</span>
                                        <ChevronRight className="w-5 h-5 text-gray-400" />
                                    </a>
                                </div>
                                <div className="py-2">
                                    <button onClick={handleSignOut} className="w-full flex items-center justify-between px-6 py-3.5 transition-colors">
                                        <span className="font-medium text-gray-900 text-[15px]">로그아웃</span>
                                        <ChevronRight className="w-5 h-5 text-gray-400" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* ===== ACCOUNT ===== */}
                    {currentView === 'account' && (
                        <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                            <div className="py-2 divide-y divide-gray-100">
                                <button
                                    onClick={() => setCurrentView('password')}
                                    className="w-full flex items-center justify-between px-6 py-3.5 transition-colors"
                                >
                                    <span className="font-medium text-gray-900 text-[15px]">비밀번호 변경</span>
                                    <ChevronRight className="w-5 h-5 text-gray-400" />
                                </button>
                                {/* 마케팅 수신 동의 토글 */}
                                <div className="w-full flex items-center justify-between px-6 py-3.5">
                                    <span className="font-medium text-gray-900 text-[15px]">마케팅 및 광고 수신 동의</span>
                                    <button
                                        onClick={handleToggleClick}
                                        disabled={isMarketingLoading}
                                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-[#F59E0B] focus:ring-offset-2 ${
                                            marketingConsent ? 'bg-[#F59E0B]' : 'bg-gray-200'
                                        } ${isMarketingLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                                        aria-label="마케팅 및 광고 수신 동의 온오프"
                                    >
                                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                            marketingConsent ? 'translate-x-6' : 'translate-x-1'
                                        }`} />
                                    </button>
                                </div>
                                <button
                                    onClick={() => { setCurrentView('delete-notice'); fetchWishlistCount() }}
                                    className="w-full flex items-center justify-between px-6 py-3.5 transition-colors"
                                >
                                    <span className="font-medium text-red-400 text-[15px]">회원 탈퇴</span>
                                    <ChevronRight className="w-5 h-5 text-gray-400" />
                                </button>
                            </div>
                        </div>
                    )}

                    {/* ===== PASSWORD CHANGE ===== */}
                    {currentView === 'password' && (
                        <section className="animate-in fade-in slide-in-from-right-4 duration-300 px-6 py-6">
                            <div className="mb-8 text-center mt-4">
                                <p className="text-gray-500 text-[15px] leading-relaxed">
                                    주기적인 비밀번호 변경을 통해<br />계정을 안전하게 보호하세요.
                                </p>
                            </div>
                            <form onSubmit={handleUpdatePassword} className="space-y-4 max-w-sm mx-auto">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-700 ml-1">현재 비밀번호</label>
                                    <Input
                                        type="password"
                                        value={currentPassword}
                                        onChange={(e) => setCurrentPassword(e.target.value)}
                                        placeholder="현재 비밀번호 입력"
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-700 ml-1">새 비밀번호</label>
                                    <Input
                                        type="password"
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        placeholder="비밀번호 입력"
                                        required
                                        minLength={8}
                                        maxLength={20}
                                    />
                                    <div className="mt-2.5 flex items-center gap-4 text-xs ml-1">
                                        <div className="flex items-center gap-1">
                                            <Check className={`w-3.5 h-3.5 ${/[a-zA-Z]/.test(newPassword) ? 'text-green-500' : 'text-gray-300'}`} />
                                            <span className={/[a-zA-Z]/.test(newPassword) ? 'text-green-600 font-medium' : 'text-gray-500'}>영문포함</span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Check className={`w-3.5 h-3.5 ${/\d/.test(newPassword) ? 'text-green-500' : 'text-gray-300'}`} />
                                            <span className={/\d/.test(newPassword) ? 'text-green-600 font-medium' : 'text-gray-500'}>숫자포함</span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Check className={`w-3.5 h-3.5 ${newPassword.length >= 8 && newPassword.length <= 20 ? 'text-green-500' : 'text-gray-300'}`} />
                                            <span className={newPassword.length >= 8 && newPassword.length <= 20 ? 'text-green-600 font-medium' : 'text-gray-500'}>8~20자 이내</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-700 ml-1">새 비밀번호 확인</label>
                                    <Input
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        placeholder="비밀번호 확인"
                                        required
                                    />
                                    <div className="mt-2.5 flex items-center gap-1 text-xs ml-1">
                                        <Check className={`w-3.5 h-3.5 ${confirmPassword.length > 0 && newPassword === confirmPassword ? 'text-green-500' : 'text-gray-300'}`} />
                                        <span className={confirmPassword.length > 0 && newPassword === confirmPassword ? 'text-green-600 font-medium' : 'text-gray-500'}>비밀번호 일치</span>
                                    </div>
                                </div>
                                {passwordMessage.text && (
                                    <p className={`text-sm ml-1 ${passwordMessage.type === 'success' ? 'text-green-600' : 'text-red-500'}`}>
                                        {passwordMessage.text}
                                    </p>
                                )}
                                <div className="pt-2">
                                    <Button
                                        type="submit"
                                        variant="primary"
                                        size="lg"
                                        disabled={
                                            isUpdatingPassword ||
                                            !currentPassword ||
                                            !newPassword ||
                                            !confirmPassword ||
                                            newPassword !== confirmPassword ||
                                            newPassword.length < 8 ||
                                            newPassword.length > 20 ||
                                            !/[a-zA-Z]/.test(newPassword) ||
                                            !/\d/.test(newPassword)
                                        }
                                        isLoading={isUpdatingPassword}
                                        className="w-full"
                                    >
                                        비밀번호 변경하기
                                    </Button>
                                </div>
                            </form>
                        </section>
                    )}

                    {/* ===== DELETE STEP 1: 유의사항 확인 ===== */}
                    {currentView === 'delete-notice' && (
                        <div className="animate-in fade-in slide-in-from-right-4 duration-300 px-6 py-6">

                            {/* 이용 현황 카드 */}
                            <div className="py-4 border-b border-gray-100 mb-6">
                                <p className="text-[13px] font-bold text-gray-800 mb-3">{user.email?.split('@')[0]}의 책자리</p>
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

                            {/* 동의 체크박스 */}
                            <label className="flex items-start gap-3 mb-8 cursor-pointer group">
                                <div
                                    className={`w-5 h-5 mt-0.5 rounded border-2 flex items-center justify-center transition-all shrink-0 ${
                                        deleteAgreed
                                            ? 'bg-[#F59E0B] border-[#F59E0B]'
                                            : 'border-gray-300 group-hover:border-[#F59E0B]'
                                    }`}
                                    onClick={() => setDeleteAgreed(!deleteAgreed)}
                                >
                                    {deleteAgreed && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                                </div>
                                <span className="text-[13px] text-gray-700 leading-relaxed">
                                    회원 탈퇴에 관한 모든 내용을 숙지하였고, 회원 탈퇴를 신청합니다.
                                </span>
                            </label>

                            {/* 하단 버튼 */}
                            <div className="flex gap-3">
                                <button
                                    onClick={() => { resetDelete(); setCurrentView('main') }}
                                    className="flex-1 py-3.5 text-gray-600 font-bold bg-gray-100 rounded-lg transition-colors text-[15px]"
                                >
                                    나중에 하기
                                </button>
                                <button
                                    disabled={!deleteAgreed}
                                    onClick={() => setCurrentView('delete-reason')}
                                    className={`flex-1 py-3.5 font-bold rounded-lg transition-colors text-[15px] ${
                                        deleteAgreed
                                            ? 'bg-[#F59E0B] text-white'
                                            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                    }`}
                                >
                                    계속 진행하기
                                </button>
                            </div>
                        </div>
                    )}

                    {/* ===== DELETE STEP 2: 탈퇴 사유 입력 ===== */}
                    {currentView === 'delete-reason' && (
                        <div className="animate-in fade-in slide-in-from-right-4 duration-300 px-6 py-6">
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
                                                deleteReason === reason
                                                    ? 'border-[#F59E0B]'
                                                    : 'border-gray-300'
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

                            {/* 기타 직접 입력 */}
                            {deleteReason === '기타(직접 작성)' && (
                                <textarea
                                    value={deleteReasonText}
                                    onChange={(e) => setDeleteReasonText(e.target.value)}
                                    placeholder="탈퇴 사유를 간략히 입력해주세요"
                                    maxLength={200}
                                    rows={4}
                                    className="w-full mb-6 px-4 py-3 border border-gray-200 rounded-lg text-[14px] text-gray-700 placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent transition"
                                />
                            )}

                            {/* 하단 버튼 */}
                            <div className="flex gap-3">
                                <button
                                    onClick={() => { resetDelete(); setCurrentView('main') }}
                                    className="flex-1 py-3.5 text-gray-600 font-bold bg-gray-100 rounded-lg transition-colors text-[15px]"
                                >
                                    나중에 하기
                                </button>
                                <button
                                    disabled={!deleteReason || (deleteReason === '기타(직접 작성)' && !deleteReasonText.trim())}
                                    onClick={() => setCurrentView('delete-password')}
                                    className={`flex-1 py-3.5 font-bold rounded-lg transition-colors text-[15px] ${
                                        deleteReason && !(deleteReason === '기타(직접 작성)' && !deleteReasonText.trim())
                                            ? 'bg-[#F59E0B] text-white'
                                            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                    }`}
                                >
                                    탈퇴하기
                                </button>
                            </div>
                        </div>
                    )}

                    {/* ===== DELETE STEP 3: 비밀번호 확인 ===== */}
                    {currentView === 'delete-password' && (
                        <section className="animate-in fade-in slide-in-from-right-4 duration-300 px-6 py-6">
                            {/* 기존 비밀번호 변경과 동일한 UI 스타일 */}
                            <div className="mb-8 text-center mt-4">
                                <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-[#FDF6E3] flex items-center justify-center">
                                    <Lock className="w-7 h-7 text-[#F59E0B]" />
                                </div>
                                <p className="text-gray-500 text-[15px] leading-relaxed">
                                    탈퇴 전 본인 확인을 위해<br />현재 비밀번호를 입력해주세요.
                                </p>
                            </div>

                            <form onSubmit={handleDeleteAccount} className="space-y-4 max-w-sm mx-auto">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-700 ml-1">
                                        비밀번호 <span className="text-red-400">*</span>
                                    </label>
                                    <Input
                                        type="password"
                                        value={deletePassword}
                                        onChange={(e) => { setDeletePassword(e.target.value); setDeletePasswordError('') }}
                                        placeholder="비밀번호 입력"
                                        required
                                    />
                                    {deletePasswordError && (
                                        <p className="text-sm text-red-500 ml-1">{deletePasswordError}</p>
                                    )}
                                </div>

                                <div className="pt-2">
                                    <Button
                                        type="submit"
                                        variant="primary"
                                        size="lg"
                                        disabled={isDeleting || !deletePassword}
                                        isLoading={isDeleting}
                                        className="w-full"
                                    >
                                        확인
                                    </Button>
                                </div>
                            </form>
                        </section>
                    )}

                </div>

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

                {/* 마케팅 수신 동의(ON) 안내 팝업 */}
                <ConfirmModal
                    isOpen={isMarketingOnNoticeOpen}
                    onClose={() => setIsMarketingOnNoticeOpen(false)}
                    onConfirm={() => executeMarketingToggle(true)}
                    title="책자리 혜택수신 동의"
                    description={
                        <div className="text-gray-600 leading-relaxed break-keep">
                            책자리를 통한 도서 추천, 프로모션 등 각종 혜택 안내 메시지를 받는 것에 동의합니다.
                        </div>
                    }
                    confirmLabel="확인"
                    cancelLabel="취소"
                    confirmVariant="primary"
                    isLoading={isMarketingLoading}
                />

                {/* 마케팅 수신 거부(OFF) 안내 팝업 */}
                <ConfirmModal
                    isOpen={isMarketingOffModalOpen}
                    onClose={() => setIsMarketingOffModalOpen(false)}
                    onConfirm={() => setIsMarketingOffModalOpen(false)}
                    title="알림"
                    description={
                        <div className="text-gray-600 leading-relaxed break-keep">
                            책자리를 통한 도서 추천, 프로모션 등 각종 혜택 안내 메시지 수신거부가 정상적으로 처리되었습니다.
                            <br /><br />
                            <span className="text-[13px]">(수신거부일 {marketingOffDate})</span>
                        </div>
                    }
                    confirmLabel="확인"
                    cancelLabel=""
                    confirmVariant="primary"
                />

                {/* 하단 토스트 팝업 */}
                <Toast
                    message={toastMessage}
                    isVisible={!!toastMessage}
                    onClose={() => setToastMessage('')}
                />

            </div>
        </main>
    )
}
