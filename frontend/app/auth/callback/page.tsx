'use client'
export const dynamic = 'force-dynamic'

import { useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { supabase } from '@/lib/supabase'

function AuthCallbackContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const step = searchParams.get('step')

    useEffect(() => {
        const handleCallback = async () => {
            const { data, error } = await supabase.auth.getSession()

            if (error) {
                console.error('Auth callback error:', error)
                router.push('/auth/signup')
                return
            }

            if (data?.session) {
                // Step 2: 약관 동의 화면으로 이동
                if (step === '2') {
                    router.push('/auth/agreements')
                } else {
                    // 기본: 홈으로 이동
                    router.push('/')
                }
            } else {
                router.push('/auth/signup')
            }
        }

        handleCallback()
    }, [router, step])

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#FF4D00] mx-auto mb-4"></div>
                <p className="text-gray-600">로그인 처리 중...</p>
            </div>
        </div>
    )
}

export default function AuthCallbackPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#FF4D00]"></div>
            </div>
        }>
            <AuthCallbackContent />
        </Suspense>
    )
}
