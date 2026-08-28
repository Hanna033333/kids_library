'use client'
export const dynamic = 'force-dynamic'

import { useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { PageLoader } from '@/components/ui/PageLoader'
import { sendGAEvent } from '@/lib/analytics'

const ADJECTIVES = ['지혜로운', '따스한', '포근한', '정겨운', '행복한', '다정한', '꿈꾸는', '다독이는', '슬기로운', '다복한', '마음넓은', '빛나는']
const NOUNS = ['책벌레', '이야기꾼', '책부엉이', '파랑새', '독서가', '책요정', '글벗', '책탐험가', '책마을님']

function generateRandomNickname() {
    const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]
    const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)]
    return `${adj}${noun}`
}

function AuthCallbackContent() {
    const router = useRouter()

    useEffect(() => {
        const handleCallback = async () => {
            const isQaMode = localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN'

            let user: any = null
            let sessionError: any = null

            if (isQaMode) {
                user = {
                    id: '00000000-0000-0000-0000-000000000000',
                    email: 'qa-tester@checkjari.com',
                    app_metadata: { provider: 'email' },
                    user_metadata: {}
                }
            } else {
                const { data: { session }, error } = await supabase.auth.getSession()
                user = session?.user ?? null
                sessionError = error
            }

            if (sessionError) {
                const msg = sessionError.message || ''
                if (msg.includes('already registered') || msg.includes('identity_already_exists')) {
                    router.push('/auth/login?error=existing_account')
                } else {
                    router.push('/auth/signup?error=auth_failed')
                }
                return
            }

            if (!user) {
                router.push('/auth/signup')
                return
            }

            // 마지막 로그인 수단 저장
            const provider = user.app_metadata?.provider
            if (provider) localStorage.setItem('last_login_provider', provider)

            sendGAEvent('login_success', { method: provider || 'unknown' })

            // QA 모드
            if (isQaMode) {
                const qaState = sessionStorage.getItem('qa_member_state')
                if (!qaState) {
                    sessionStorage.setItem('qa_member_state', 'registered')
                    sessionStorage.setItem('showSignupComplete', 'true')
                    const nickname = generateRandomNickname()
                    sessionStorage.setItem('generatedNickname', nickname)
                }
                const returnUrl = sessionStorage.getItem('returnUrl')
                sessionStorage.removeItem('returnUrl')
                window.location.replace(returnUrl || '/')
                return
            }

            // 기존 회원 여부 확인
            const { data: member, error: memberError } = await supabase
                .from('members')
                .select('id, nickname')
                .eq('id', user.id)
                .single()

            if (memberError && memberError.code !== 'PGRST116') {
                console.error('Error fetching member:', memberError)
            }

            const isNewUser = !member

            if (isNewUser) {
                // 신규 유저: 자동 회원가입 처리
                const nickname = generateRandomNickname()
                sessionStorage.setItem('generatedNickname', nickname)

                const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                const API_BASE_URL = isLocal
                    ? 'http://127.0.0.1:8000'
                    : (process.env.NEXT_PUBLIC_API_URL || 'https://api.checkjari.com')

                const { data: sessionData } = await supabase.auth.getSession()
                const token = sessionData?.session?.access_token || ''

                try {
                    await fetch(`${API_BASE_URL}/api/auth/me/agreements`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            agreed_to_terms: true,
                            agreed_to_privacy: true,
                            agreed_to_marketing: false,
                            nickname
                        })
                    })
                } catch (e) {
                    console.error('Auto-registration failed:', e)
                }

                sendGAEvent('sign_up', { method: provider || 'unknown' })
                sessionStorage.setItem('showSignupComplete', 'true')
            }

            const returnUrl = sessionStorage.getItem('returnUrl')
            sessionStorage.removeItem('returnUrl')
            window.location.replace(returnUrl || '/')
        }

        handleCallback()
    }, [router])

    return <PageLoader />
}

export default function AuthCallbackPage() {
    return (
        <Suspense fallback={<PageLoader />}>
            <AuthCallbackContent />
        </Suspense>
    )
}
