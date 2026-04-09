'use client'

import { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'
import { Check, ChevronLeft } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import PageHeader from '@/components/PageHeader'
import { sendGAEvent } from '@/lib/analytics'

export default function SetPasswordPage() {
    const router = useRouter()
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const { user: authUser } = useAuth()
    
    // 실시간 유효성 검사 상태
    const validation = useMemo(() => {
        return {
            hasLetter: /[a-zA-Z]/.test(password),
            hasNumber: /[0-9]/.test(password),
            isLengthValid: password.length >= 8 && password.length <= 20,
            isMatch: password !== '' && password === confirmPassword
        }
    }, [password, confirmPassword])

    const isValid = validation.hasLetter && validation.hasNumber && validation.isLengthValid && validation.isMatch

    const handleComplete = async () => {
        if (!isValid) return

        setLoading(true)
        setError('')

        try {
            // Use authUser from context instead of directly calling supabase.auth.getUser()
            // to support QA mock sessions
            const user = authUser;

            if (!user) {
                throw new Error('User not found')
            }

            // Only update password if not in QA mode (or handle differently)
            const isQaMode = typeof window !== 'undefined' && localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN';
            
            if (!isQaMode) {
                const { error: updateError } = await supabase.auth.updateUser({
                    password: password
                })

                if (updateError) {
                    if (updateError.message.includes('different from the old password')) {
                        console.log('Password is unchanged (same as previous). Proceeding.')
                    } else {
                        console.error('Password update failed:', updateError.message)
                        let msg = updateError.message
                        if (msg.includes('weak')) msg = '비밀번호가 너무 쉽습니다. 더 복잡하게 설정해주세요.'
                        else if (msg.includes('same')) msg = '이전과 다른 비밀번호를 설정해주세요.'
                        throw new Error(`비밀번호 설정 실패: ${msg}`)
                    }
                }
            }

            const agreementsStr = sessionStorage.getItem('signup_agreements')
            const agreements = agreementsStr ? JSON.parse(agreementsStr) : {}

            const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            const API_BASE_URL = isLocal ? "http://127.0.0.1:8000" : (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000");

            let authToken = '';
            if (isQaMode) {
                authToken = 'TEST_QA_TOKEN';
            } else {
                const { data: sessionData } = await supabase.auth.getSession();
                authToken = sessionData.session?.access_token || '';
            }

            const response = await fetch(`${API_BASE_URL}/api/auth/me/agreements`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    agreed_to_terms: agreements.termsAgreed || false,
                    agreed_to_privacy: agreements.privacyAgreed || false,
                    agreed_to_marketing: agreements.marketingAgreed || false
                })
            })

            if (!response.ok) {
                const errorText = await response.text()
                throw new Error(`Failed to save agreements (${response.status}): ${errorText}`)
            }

            // Track GA Sign-up event
            sendGAEvent('sign_up', { 
                method: agreements.marketingAgreed ? 'with_marketing' : 'without_marketing' 
            })

            sessionStorage.removeItem('signup_agreements')

            const returnUrl = sessionStorage.getItem('returnUrl')
            if (returnUrl) {
                router.push(returnUrl)
            } else {
                router.push('/')
            }
        } catch (err: any) {
            if (err.message === 'User not found') {
                setError('로그인이 필요합니다.')
            } else if (err.message === 'Failed to fetch') {
                setError('회원 가입에 문제가 있습니다. 잠시 후 다시 시도해주세요.')
            } else {
                setError(err.message || '회원가입 완료 중 오류가 발생했습니다.')
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-white font-sans flex flex-col items-center">
            {/* 상단 헤더 */}
            <PageHeader
                title=""
                backHref="/auth/agreements"
                rightSlot={null}
            />

            <div className="w-full max-w-sm flex flex-col items-center px-6 pb-12 pt-12">
                {/* 헤더 */}
                <div className="mb-10 text-center flex flex-col items-center">
                    <img
                        src="/logo.png"
                        alt="책자리"
                        className="w-16 h-auto mb-6"
                    />
                    <h1 className="text-[26px] font-bold text-gray-900 leading-tight mb-3 tracking-tight">
                        비밀번호 설정
                    </h1>
                    <p className="text-gray-500 text-[15px] leading-relaxed">
                        안전한 서비스 이용을 위해<br />
                        비밀번호를 설정해 주세요
                    </p>
                </div>

                {/* 입력 카드 영역 */}
                <div className="w-full bg-gray-50/50 rounded-[24px] p-6 mb-8 border border-gray-100/50 space-y-8">
                    {/* 비밀번호 입력 */}
                    <div className="space-y-3">
                        <input
                            type="password"
                            placeholder="비밀번호 입력"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full h-[56px] px-5 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-primary focus:border-brand-primary transition-all text-[16px]"
                        />
                        <div className="flex flex-wrap gap-x-4 gap-y-2 px-1">
                            <div className="flex items-center gap-1">
                                <span className={`text-[13px] ${validation.hasLetter ? 'text-gray-900 font-medium' : 'text-gray-400'}`}>영문포함</span>
                                <Check className={`w-4 h-4 stroke-[1.5] ${validation.hasLetter ? 'text-brand-primary' : 'text-gray-200'}`} />
                            </div>
                            <div className="flex items-center gap-1">
                                <span className={`text-[13px] ${validation.hasNumber ? 'text-gray-900 font-medium' : 'text-gray-400'}`}>숫자포함</span>
                                <Check className={`w-4 h-4 stroke-[1.5] ${validation.hasNumber ? 'text-brand-primary' : 'text-gray-200'}`} />
                            </div>
                            <div className="flex items-center gap-1">
                                <span className={`text-[13px] ${validation.isLengthValid ? 'text-gray-900 font-medium' : 'text-gray-400'}`}>8~20자 이내</span>
                                <Check className={`w-4 h-4 stroke-[1.5] ${validation.isLengthValid ? 'text-brand-primary' : 'text-gray-200'}`} />
                            </div>
                        </div>
                    </div>

                    {/* 비밀번호 확인 */}
                    <div className="space-y-3">
                        <input
                            type="password"
                            placeholder="비밀번호 확인"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className="w-full h-[56px] px-5 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-primary focus:border-brand-primary transition-all text-[16px]"
                        />
                        <div className="flex items-center gap-1 px-1">
                            <span className={`text-[13px] ${validation.isMatch ? 'text-gray-900 font-medium' : 'text-gray-400'}`}>비밀번호 일치</span>
                            <Check className={`w-4 h-4 stroke-[1.5] ${validation.isMatch ? 'text-brand-primary' : 'text-gray-200'}`} />
                        </div>
                    </div>

                    {error && (
                        <p className="text-[13px] text-red-500 font-medium px-1">{error}</p>
                    )}
                </div>

                <div className="w-full mt-auto">
                    <Button
                        onClick={handleComplete}
                        disabled={loading || !isValid}
                        isLoading={loading}
                        variant="primary"
                        size="lg"
                        className={`w-full rounded-lg h-[56px] text-lg font-bold transition-all
                            ${isValid
                                ? 'bg-[#F59E0B] text-white'
                                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            }`}
                    >
                        완료
                    </Button>
                </div>
            </div>
        </div>
    )
}
