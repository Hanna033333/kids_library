'use client'

import { useState, useMemo, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'
import { Check } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import PageHeader from '@/components/PageHeader'
import { sendGAEvent } from '@/lib/analytics'

// 책/육아 관련 한글 형용사 + 명사 랜덤 닉네임 생성기 (띄어쓰기 없음)
const ADJECTIVES = ['지혜로운', '따스한', '포근한', '정겨운', '행복한', '다정한', '꿈꾸는', '다독이는', '슬기로운', '다복한', '마음넓은', '빛나는']
const NOUNS = ['책벌레', '이야기꾼', '책부엉이', '파랑새', '독서가', '책요정', '글벗', '책탐험가', '책마을님']

function generateRandomNickname() {
    const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]
    const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)]
    return `${adj}${noun}`
}

export default function SetPasswordPage() {
    const router = useRouter()
    const [nickname, setNickname] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const { user: authUser } = useAuth()

    // 닉네임 초기화 (OAuth 메타데이터 수집 시도 -> 없으면 랜덤 형용사+명사 생성, 띄어쓰기 제거)
    useEffect(() => {
        const rawExistingName =
            authUser?.user_metadata?.full_name ||
            authUser?.user_metadata?.name ||
            authUser?.user_metadata?.nickname

        const existingName = rawExistingName ? rawExistingName.replace(/\s+/g, '') : ''

        if (existingName && existingName.length >= 2 && existingName.length <= 10) {
            setNickname(existingName)
        } else {
            setNickname(generateRandomNickname())
        }
    }, [authUser])

    // 실시간 유효성 검사 상태
    const validation = useMemo(() => {
        return {
            hasLetter: /[a-zA-Z]/.test(password),
            hasNumber: /[0-9]/.test(password),
            isLengthValid: password.length >= 8 && password.length <= 20,
            isMatch: password !== '' && password === confirmPassword
        }
    }, [password, confirmPassword])

    const isValid =
        validation.hasLetter &&
        validation.hasNumber &&
        validation.isLengthValid &&
        validation.isMatch

    const handleComplete = async () => {
        if (!isValid) return

        setLoading(true)
        setError('')

        try {
            const user = authUser

            if (!user) {
                throw new Error('User not found')
            }

            const isQaMode = typeof window !== 'undefined' && localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN'
            const finalNickname = nickname.trim() || generateRandomNickname()

            if (!isQaMode) {
                // 비밀번호 및 유저 메타데이터(닉네임) 업데이트
                const { error: updateError } = await supabase.auth.updateUser({
                    password: password,
                    data: {
                        nickname: finalNickname,
                        full_name: finalNickname
                    }
                })

                if (updateError) {
                    if (updateError.message.includes('different from the old password')) {
                        console.log('Password is unchanged (same as previous). Proceeding.')
                    } else {
                        console.error('Password update failed:', updateError.message)
                        let msg = updateError.message
                        if (msg.includes('weak')) msg = '비밀번호가 너무 쉽습니다. 더 복잡하게 설정해주세요.'
                        else if (msg.includes('same')) msg = '이전과 다른 비밀번호를 설정해주세요.'
                        throw new Error(`정보 설정 실패: ${msg}`)
                    }
                }
            }

            const agreementsStr = sessionStorage.getItem('signup_agreements')
            const agreements = agreementsStr ? JSON.parse(agreementsStr) : {}

            const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            const API_BASE_URL = isLocal ? "http://127.0.0.1:8000" : (process.env.NEXT_PUBLIC_API_URL || "https://api.checkjari.com")

            let authToken = ''
            if (isQaMode) {
                authToken = 'TEST_QA_TOKEN'
            } else {
                const { data: sessionData } = await supabase.auth.getSession()
                authToken = sessionData.session?.access_token || ''
            }

            // 약관 동의는 Step 4(/auth/agreements)에서 이미 저장됨
            // 여기서는 닉네임만 PATCH로 업데이트
            const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    nickname: finalNickname
                })
            })

            if (!response.ok) {
                const errorText = await response.text()
                throw new Error(`닉네임 저장 실패 (${response.status}): ${errorText}`)
            }

            // Track GA Sign-up event
            sendGAEvent('sign_up', { 
                method: agreements.marketingAgreed ? 'with_marketing' : 'without_marketing' 
            })

            sessionStorage.removeItem('signup_agreements')

            const returnUrl = sessionStorage.getItem('returnUrl')
            sessionStorage.setItem('showSignupComplete', 'true')
            if (returnUrl) {
                sessionStorage.removeItem('returnUrl')
                window.location.href = returnUrl
            } else {
                window.location.href = '/'
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
                backHref="/"
                rightSlot={null}
            />

            <div className="w-full max-w-sm flex flex-col items-center px-6 pb-12 pt-8">
                {/* 헤더 */}
                <div className="mb-8 text-center flex flex-col items-center">
                    <img
                        src="/logo.png"
                        alt="책자리"
                        className="w-14 h-auto mb-5"
                    />
                    <h1 className="text-[24px] font-bold text-gray-900 leading-tight mb-2 tracking-tight">
                        비밀번호 설정
                    </h1>
                    <p className="text-gray-500 text-[14px] leading-relaxed">
                        책자리에서 사용할 비밀번호를 설정해 주세요
                    </p>
                </div>

                {/* 입력 카드 영역 */}
                <form onSubmit={(e) => e.preventDefault()} autoComplete="off" className="w-full bg-gray-50/50 rounded-[24px] p-6 mb-8 border border-gray-100/50 space-y-6">
                    {/* 비밀번호 입력 */}
                    <div className="space-y-2">
                        <label className="block text-xs font-bold text-gray-500 px-1">
                            비밀번호
                        </label>
                        <input
                            type="password"
                            placeholder="비밀번호 입력"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            autoComplete="new-password"
                            className="w-full h-[54px] px-4 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-brand-primary focus:border-brand-primary transition-all text-[15px]"
                        />
                        <div className="flex flex-wrap gap-x-3 gap-y-1.5 px-1 pt-1">
                            <div className="flex items-center gap-1">
                                <span className={`text-[12px] ${validation.hasLetter ? 'text-green-600 font-medium' : 'text-gray-400'}`}>영문포함</span>
                                <Check className={`w-3.5 h-3.5 stroke-[2] ${validation.hasLetter ? 'text-green-500' : 'text-gray-200'}`} />
                            </div>
                            <div className="flex items-center gap-1">
                                <span className={`text-[12px] ${validation.hasNumber ? 'text-green-600 font-medium' : 'text-gray-400'}`}>숫자포함</span>
                                <Check className={`w-3.5 h-3.5 stroke-[2] ${validation.hasNumber ? 'text-green-500' : 'text-gray-200'}`} />
                            </div>
                            <div className="flex items-center gap-1">
                                <span className={`text-[12px] ${validation.isLengthValid ? 'text-green-600 font-medium' : 'text-gray-400'}`}>8~20자 이내</span>
                                <Check className={`w-3.5 h-3.5 stroke-[2] ${validation.isLengthValid ? 'text-green-500' : 'text-gray-200'}`} />
                            </div>
                        </div>
                    </div>

                    {/* 비밀번호 확인 */}
                    <div className="space-y-2">
                        <input
                            type="password"
                            placeholder="비밀번호 확인"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            autoComplete="new-password"
                            className="w-full h-[54px] px-4 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-brand-primary focus:border-brand-primary transition-all text-[15px]"
                        />
                        <div className="flex items-center gap-1 px-1">
                            <span className={`text-[12px] ${validation.isMatch ? 'text-green-600 font-medium' : 'text-gray-400'}`}>비밀번호 일치</span>
                            <Check className={`w-3.5 h-3.5 stroke-[2] ${validation.isMatch ? 'text-green-500' : 'text-gray-200'}`} />
                        </div>
                    </div>

                    {error && (
                        <p className="text-[13px] text-red-500 font-medium px-1">{error}</p>
                    )}
                </form>

                <div className="w-full mt-auto">
                    <Button
                        onClick={handleComplete}
                        disabled={loading || !isValid}
                        isLoading={loading}
                        variant="primary"
                        size="lg"
                        className={`w-full rounded-xl h-[54px] text-base font-bold transition-all
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

