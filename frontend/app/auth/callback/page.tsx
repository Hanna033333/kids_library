'use client'

import { useEffect } from 'react'
import { createClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import { Loader2 } from 'lucide-react'

export default function AuthCallback() {
    const router = useRouter()
    const supabase = createClient()

    useEffect(() => {
        const handleCallback = async () => {
            const { error } = await supabase.auth.exchangeCodeForSession(
                window.location.search.split('code=')[1]?.split('&')[0] || ''
            )

            if (!error) {
                router.push('/')
            } else {
                console.error('Auth callback error:', error)
                router.push('/auth?error=callback_failed')
            }
        }

        handleCallback()
    }, [router, supabase.auth])

    return (
        <div className="min-h-screen bg-[#F7F7F7] flex flex-col items-center justify-center p-4">
            <Loader2 className="w-10 h-10 text-blue-600 animate-spin mb-4" />
            <p className="text-gray-600 font-medium text-lg">로그인 준비 중입니다...</p>
        </div>
    )
}
