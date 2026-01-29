'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import { LogIn, UserPlus, Mail, Lock, Loader2 } from 'lucide-react'

export default function AuthClient() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [isSignUp, setIsSignUp] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const router = useRouter()
    const supabase = createClient()

    // 베타 기간 접근 제한
    useEffect(() => {
        alert('베타 기간에는 로그인 및 회원가입을 지원하지 않습니다.');
        router.push('/');
    }, [router]);


    const handleAuth = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)
        setError(null)

        try {
            if (isSignUp) {
                const { error } = await supabase.auth.signUp({
                    email,
                    password,
                    options: {
                        emailRedirectTo: `${window.location.origin}/auth/callback`,
                    },
                })
                if (error) throw error
                alert('가입 확인 이메일을 보냈습니다. 이메일을 확인해주세요!')
            } else {
                const { error } = await supabase.auth.signInWithPassword({
                    email,
                    password,
                })
                if (error) throw error
                router.push('/')
                router.refresh()
            }
        } catch (err: any) {
            setError(err.message || '인증에 실패했습니다.')
        } finally {
            setIsLoading(false)
        }
    }

    const handleKakaoLogin = async () => {
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'kakao',
                options: {
                    redirectTo: `${window.location.origin}/auth/callback`,
                },
            })
            if (error) throw error
        } catch (err: any) {
            setError('카카오 로그인 설정이 필요합니다.')
        }
    }

    return (
        <div className="min-h-screen bg-[#F7F7F7] flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white rounded-xl shadow-xl overflow-hidden border border-gray-100">
                <div className="p-8">
                    <div className="text-center mb-10">
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">
                            {isSignUp ? '반가워요!' : '다시 만났네요!'}
                        </h1>
                        <p className="text-gray-500">
                            우리 아이 도서관 서비스를 시작해보세요
                        </p>
                    </div>

                    <form onSubmit={handleAuth} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700 ml-1">이메일</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                                    placeholder="example@email.com"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700 ml-1">비밀번호</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        {error && (
                            <p className="text-sm text-red-500 ml-1">{error}</p>
                        )}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-[#F59E0B] hover:bg-[#D97706] text-white font-semibold py-3 rounded-lg shadow-lg shadow-gray-200 transition-all flex items-center justify-center gap-2 group"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : isSignUp ? (
                                '회원가입하기'
                            ) : (
                                '로그인'
                            )}
                        </button>
                    </form>

                    <div className="mt-8">
                        <div className="relative mb-6">
                            <div className="absolute inset-0 flex items-center">
                                <div className="w-full border-t border-gray-100"></div>
                            </div>
                            <div className="relative flex justify-center text-sm">
                                <span className="px-2 bg-white text-gray-400">또는</span>
                            </div>
                        </div>

                        <button
                            onClick={handleKakaoLogin}
                            className="w-full bg-[#FEE500] hover:bg-[#FDE000] text-[#191919] font-semibold py-3 rounded-lg transition-all flex items-center justify-center gap-3"
                        >
                            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 3c-4.97 0-9 3.11-9 6.94 0 2.42 1.58 4.54 3.96 5.8l-.94 3.44c-.06.21.05.4.24.46.06.02.12.03.18.03.13 0 .25-.07.32-.2l4.08-2.7c.38.04.77.07 1.16.07 4.97 0 9-3.11 9-6.94S16.97 3 12 3z" />
                            </svg>
                            카카오로 시작하기
                        </button>
                    </div>

                    <p className="mt-8 text-center text-sm text-gray-500">
                        {isSignUp ? '이미 계정이 있으신가요?' : '아직 계정이 없으신가요?'}
                        <button
                            onClick={() => setIsSignUp(!isSignUp)}
                            className="ml-2 text-gray-900 font-semibold underline"
                        >
                            {isSignUp ? '로그인' : '회원가입'}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    )
}
