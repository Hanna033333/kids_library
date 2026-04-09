'use client'
export const dynamic = 'force-dynamic'

import { useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { Spinner } from '@/components/ui/Spinner'
import { PageLoader } from '@/components/ui/PageLoader'
import { sendGAEvent } from '@/lib/analytics'

function AuthCallbackContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const step = searchParams.get('step')

    useEffect(() => {
        const handleCallback = async () => {
            let sessionData: any = null;
            let sessionError: any = null;

            // QA 모드 체크
            const isQaMode = localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN';

            if (isQaMode) {
                sessionData = {
                    user: {
                        id: '00000000-0000-0000-0000-000000000000',
                        email: 'qa-tester@checkjari.com'
                    }
                };
            } else {
                const { data: { session }, error } = await supabase.auth.getSession();
                sessionData = session;
                sessionError = error;
            }

            if (sessionError) {
                console.error('Auth callback session error:', sessionError)
                
                // 에러 메시지나 URL 파라미터에서 이메일 정보가 있는지 확인 (Supabase 에러 객체 구조에 따라 다름)
                // 만약 에러 발생 시점에 이메일을 알 수 없다면, 일반적인 에러 메시지만 전달
                const errorMsg = sessionError.message || '';
                if (errorMsg.includes('already registered') || errorMsg.includes('identity_already_exists')) {
                    router.push('/auth/login?error=existing_account')
                } else {
                    router.push('/auth/signup?error=auth_failed')
                }
                return
            }

            const user = sessionData?.user;

            if (user) {
                // 마지막 로그인 수단 저장
                const provider = user.app_metadata?.provider
                if (provider) {
                    localStorage.setItem('last_login_provider', provider)
                }

                // Track GA Login success
                sendGAEvent('login_success', { method: provider || 'unknown' })

                // Check if user is already registered in members table
                const { data: member, error: memberError } = await supabase
                    .from('members')
                    .select('agreed_to_terms')
                    .eq('id', user.id)
                    .single()

                if (memberError && memberError.code !== 'PGRST116') { // PGRST116: no rows returned
                    console.error('Error fetching member status:', memberError)
                }

                // If user has already agreed to terms, they are an existing user
                if (member?.agreed_to_terms) {
                    const returnUrl = sessionStorage.getItem('returnUrl')
                    sessionStorage.removeItem('returnUrl') // Clean up
                    router.push(returnUrl || '/')
                    return
                }

                // If user hasn't agreed to terms, they need to go to agreements page
                if (!member?.agreed_to_terms) {
                    router.push('/auth/agreements')
                    return
                }

                // Existing user: go to returnUrl or home
                const returnUrl = sessionStorage.getItem('returnUrl')
                sessionStorage.removeItem('returnUrl')
                router.push(returnUrl || '/')
            } else {
                router.push('/auth/signup')
            }
        }

        handleCallback()
    }, [router, step])

    return (
        <PageLoader />
    )
}

export default function AuthCallbackPage() {
    return (
        <Suspense fallback={<PageLoader />}>
            <AuthCallbackContent />
        </Suspense>
    )
}
