'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { PageLoader } from '@/components/ui/PageLoader'
import { sendGAEvent } from '@/lib/analytics'


export default function AuthClient() {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [lastProvider, setLastProvider] = useState<string | null>(null)
    const router = useRouter()
    const searchParams = useSearchParams()
    const supabase = createClient()

    useEffect(() => {
        // 로컬스토리지에서 마지막 로그인 수단 가져오기
        const savedProvider = localStorage.getItem('last_login_provider')
        if (savedProvider) {
            setLastProvider(savedProvider)
        }

        // URL 파라미터에서 에러 확인 (이메일 중복 등)
        const errorCode = searchParams.get('error')
        if (errorCode === 'existing_account') {
            setError('동일한 이메일로 이미 가입된 기록이 있습니다. 다른 소셜 로그인(카카오/구글)을 시도해 보세요.')
        } else if (errorCode === 'auth_failed') {
            setError('로그인 처리 중 오류가 발생했습니다. 다시 시도해 주세요.')
        }
    }, [searchParams])

    const handleKakaoLogin = async () => {
        setIsLoading(true)
        setError(null)
        sendGAEvent('login_attempt', { method: 'kakao' })
        localStorage.setItem('last_login_provider', 'kakao')
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'kakao',
                options: {
                    redirectTo: `${window.location.origin}/auth/callback?step=2`,
                },
            })
            if (error) throw error
        } catch (err: any) {
            setError('카카오 로그인 중 오류가 발생했습니다.')
            setIsLoading(false)
        }
    }

    const handleGoogleLogin = async () => {
        setIsLoading(true)
        setError(null)
        sendGAEvent('login_attempt', { method: 'google' })
        localStorage.setItem('last_login_provider', 'google')
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: `${window.location.origin}/auth/callback?step=2`,
                },
            })
            if (error) throw error
        } catch (err: any) {
            setError('구글 로그인 중 오류가 발생했습니다.')
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-white px-6 pb-20">
            <div className="w-full max-w-[320px] flex flex-col items-center text-center">
                {/* 로고 */}
                <img
                    src="/logo.png"
                    alt="책자리"
                    className="w-16 h-auto mb-8"
                />

                {/* USP 텍스트 */}
                <div className="space-y-3 mb-12">
                    <h1 className="text-2xl font-bold text-gray-900 leading-snug whitespace-pre-wrap">
                        도서관 헛걸음은 그만,{'\n'}
                        책자리로 확인하세요!
                    </h1>
                    <p className="text-gray-500 text-sm leading-relaxed whitespace-pre-wrap">
                        우리 아이 맞춤 도서 추천부터{'\n'}
                        대출 가능 여부까지 한 번에
                    </p>
                </div>

                {/* 에러 메시지 표시 */}
                {error && (
                    <div className="w-full mb-6 p-4 bg-red-50 border border-red-100 rounded-lg">
                        <p className="text-sm text-red-600 font-medium">{error}</p>
                    </div>
                )}

                {/* 소셜 로그인 버튼 */}
                <div className="w-full space-y-4">
                    {/* 카카오 로그인 */}
                    <div className="relative pt-2">
                        {lastProvider === 'kakao' && (
                            <div className="absolute -top-1 right-0 z-10">
                                <span className="bg-brand-primary text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm">
                                    마지막 로그인
                                </span>
                            </div>
                        )}
                        <Button
                            onClick={handleKakaoLogin}
                            variant="kakao"
                            size="lg"
                            disabled={isLoading}
                            className="w-full relative py-7"
                        >
                            <div className="absolute left-6">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 3C5.373 3 0 7.373 0 12.765c0 3.39 2.15 6.42 5.513 8.212l-1.092 4.098c-.12.45.33.84.72.63l4.62-2.31c.712.09 1.442.138 2.18.138 6.627 0 12-4.373 12-9.765C24 7.373 18.627 3 12 3z" />
                                </svg>
                            </div>
                            <span className="text-[16px] font-semibold">카카오로 로그인</span>
                        </Button>
                    </div>

                    {/* 구글 로그인 */}
                    <div className="relative pt-2">
                        {lastProvider === 'google' && (
                            <div className="absolute -top-1 right-0 z-10">
                                <span className="bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm">
                                    마지막 로그인
                                </span>
                            </div>
                        )}
                        <Button
                            onClick={handleGoogleLogin}
                            variant="secondary"
                            size="lg"
                            disabled={isLoading}
                            className="w-full relative py-7 border-gray-200"
                        >
                            <div className="absolute left-6">
                                <svg width="20" height="20" viewBox="0 0 24 24">
                                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                                </svg>
                            </div>
                            <span className="text-[16px] font-semibold">Google로 로그인</span>
                        </Button>
                    </div>

                    {/* QA 테스터 로그인 (개발 환경 전용) */}
                    {process.env.NODE_ENV === 'development' && (
                        <Button
                            onClick={() => {
                                localStorage.setItem('supabase.auth.token', 'TEST_QA_TOKEN');
                                sessionStorage.setItem('qa_mode', 'true');
                                router.push('/auth/callback?step=2');
                            }}
                            variant="outline"
                            size="lg"
                            className="w-full py-7 border-dashed border-2 border-brand-primary text-brand-primary mt-2"
                        >
                            <span className="text-[16px] font-bold">QA 테스터로 로그인 (개발용)</span>
                        </Button>
                    )}
                </div>
            </div>
            {isLoading && <PageLoader />}
        </div>
    )
}
