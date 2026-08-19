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
                let member: { agreed_to_terms: boolean; nickname: string | null } | null = null

                if (isQaMode) {
                    const qaState = sessionStorage.getItem('qa_member_state')
                    if (qaState === 'step4_done') {
                        member = { agreed_to_terms: true, nickname: null }
                    } else if (qaState === 'step5_done') {
                        member = { agreed_to_terms: true, nickname: 'QA테스터' }
                    } else {
                        member = null
                    }
                } else {
                    const { data, error: memberError } = await supabase
                        .from('members')
                        .select('agreed_to_terms, nickname')
                        .eq('id', user.id)
                        .single()

                    if (memberError && memberError.code !== 'PGRST116') {
                        console.error('Error fetching member status:', memberError)
                    }
                    member = data
                }

                // 분기 1: 레코드 없음 or 약관 미동의 → 약관 동의 화면
                if (!member || !member.agreed_to_terms) {
                    window.location.replace('/auth/agreements')
                    return
                }

                // 분기 2: 약관 동의 완료 + 닉네임 미설정 → Step 5 (4~5 이탈 후 재진입)
                if (member.agreed_to_terms && !member.nickname) {
                    window.location.replace('/auth/set-password')
                    return
                }

                // 분기 3: 완전 가입 완료 → 홈 or returnUrl
                const returnUrl = sessionStorage.getItem('returnUrl')
                sessionStorage.removeItem('returnUrl')
                window.location.replace(returnUrl || '/')
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
