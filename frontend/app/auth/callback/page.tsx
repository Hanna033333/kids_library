'use client'
export const dynamic = 'force-dynamic'

import { useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { PageLoader } from '@/components/ui/PageLoader'
import { sendGAEvent, sendGAEventAndRedirect } from '@/lib/analytics'

const ADJECTIVES = [
    '지혜로운', '따스한', '포근한', '정겨운', '행복한', '다정한', '꿈꾸는', '다독이는', '슬기로운', '다복한', 
    '마음넓은', '빛나는', '즐거운', '상냥한', '반짝이는', '용감한', '푸른', '희망찬', '해맑은', '고마운', 
    '포근포근', '싱그러운', '너그러운', '새싹같은', '옹달샘', '보드라운', '초롱초롱', '알록달록', '은은한', '산뜻한',
    '사랑스런', '명랑한', '슬기찬', '어질고', '호기심찬', '눈부신', '도란도란', '달콤한', '미소짓는', '소담한',
    '재치있는', '기운찬', '활기찬', '따사로운', '아늑한', '별처럼', '구름같은', '무지개빛', '정다운', '온화한',
    '단단한', '자유로운', '맑고밝은', '조잘조잘', '살가운', '도란대는', '생글생글', '두근두근', '소복소복', '풍성한',
    '향기로운', '든든한', '기쁨가득', '마음고운', '생각깊은', '지혜가득', '꿈이많은', '찬란한', '싱글벙글', '방긋웃는',
    '풋풋한', '순수한', '맑은눈의', '꿈꾸듯', '솔솔부는', '똘똘한', '야무진', '의젓한', '씩씩한', '반듯한'
]
const NOUNS = [
    '책벌레', '이야기꾼', '책부엉이', '파랑새', '독서가', '책요정', '글벗', '책탐험가', '책마을님', '도토리',
    '꿈나무', '독서왕', '별나무', '책친구', '아기도깨비', '책다람쥐', '토끼', '작은새', '어린사자', '꼬마곰',
    '책박사', '길잡이', '책마법사', '글마루', '책지기', '동화작가', '숲속요정', '별똥별', '새싹', '햇살이',
    '달팽이', '꽃사슴', '아기호랑이', '책누리', '글꽃', '책별', '은하수', '숲속친구', '이야기샘', '책방주인',
    '글타래', '책등대', '지혜샘', '달맞이', '별지기', '숲지기', '꿈꾸미', '도서관지기', '글동무', '책풍경',
    '호기심대장', '상상왕', '생각나무', '독서대장', '마음상자', '이야기별', '책바다', '단풍잎', '은행잎', '솔방울',
    '아기참새', '책정원', '글나라', '동화나무', '책소리', '글소리', '달빛요정', '별빛마을', '작은여우', '아기달님',
    '숲속곰돌이', '꼬마별', '책마중', '글나래', '꿈나래', '새싹지기', '솔바람', '들꽃', '책보따리', '이야기꽃'
]

function generateRandomNickname() {
    const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]
    const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)]
    const randNum = Math.floor(100 + Math.random() * 900)
    return `${adj}${noun}${randNum}`
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

            // 이메일 미제공 계정 차단.
            // members.email은 NOT NULL이라 이메일 없이는 회원 레코드를 만들 수 없다.
            // 그대로 두면 "인증은 됐는데 아무 기능도 안 되는" 상태로 방치되므로,
            // 세션을 정리하고 사유를 알린 뒤 가입을 중단시킨다.
            if (!isQaMode && !user.email) {
                sendGAEvent('signup_blocked_no_email', { method: provider || 'unknown' })
                await supabase.auth.signOut()
                router.replace('/auth?error=email_required')
                return
            }

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

            sendGAEvent('login_success', { method: provider || 'unknown' })

            // 기존 회원 여부 확인
            const { data: member, error: memberError } = await supabase
                .from('members')
                .select('id, nickname')
                .eq('id', user.id)
                .single()

            if (memberError && memberError.code !== 'PGRST116') {
                console.error('Error fetching member:', memberError)
            }

            // DB 트리거(023)가 auth.users 생성 시 members 행을 먼저 만들기 때문에
            // '행이 없다'로는 신규 가입을 판별할 수 없다. 두 가지를 나눠서 본다.
            //  - needsProfile     : 닉네임이 비어 프로필 채우기가 필요한가 (트리거 유무와 무관하게 동작)
            //  - isBrandNewAccount: 방금 만들어진 계정인가 (축하 모달·sign_up 집계 기준)
            const needsProfile = !member || !member.nickname
            const accountAgeMs = user.created_at
                ? Date.now() - new Date(user.created_at).getTime()
                : Number.POSITIVE_INFINITY
            const isBrandNewAccount = accountAgeMs < 5 * 60 * 1000
            let registered = false

            if (needsProfile) {
                // 신규 유저: 자동 회원가입 처리
                const nickname = generateRandomNickname()
                sessionStorage.setItem('generatedNickname', nickname)

                const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                const API_BASE_URL = isLocal
                    ? 'http://127.0.0.1:8000'
                    : (process.env.NEXT_PUBLIC_API_URL || 'https://api.checkjari.com')

                const { data: sessionData } = await supabase.auth.getSession()
                const token = sessionData?.session?.access_token || ''

                // 백엔드 응답이 지연돼도 로더에 갇히지 않도록 8초 타임아웃을 건다
                const registerMember = async (): Promise<{ ok: boolean; status: number; reason: string }> => {
                    const controller = new AbortController()
                    const timer = setTimeout(() => controller.abort(), 8000)
                    try {
                        const res = await fetch(`${API_BASE_URL}/api/auth/me/agreements`, {
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
                            }),
                            signal: controller.signal
                        })
                        if (res.ok) return { ok: true, status: res.status, reason: '' }
                        // fetch는 4xx/5xx에 throw하지 않으므로 status를 직접 확인해야 실패를 잡을 수 있다
                        const body = await res.text().catch(() => '')
                        return { ok: false, status: res.status, reason: body.slice(0, 120) }
                    } catch (e: any) {
                        return {
                            ok: false,
                            status: 0,
                            reason: e?.name === 'AbortError' ? 'timeout' : (e?.message || 'network_error')
                        }
                    } finally {
                        clearTimeout(timer)
                    }
                }

                // 일시적인 네트워크 오류로 가입이 통째로 유실되지 않도록 1회 재시도
                let result = await registerMember()
                if (!result.ok) result = await registerMember()
                registered = result.ok

                if (!result.ok) {
                    console.error(`Auto-registration failed (status=${result.status}): ${result.reason}`)
                    // 가입 실패를 GA에 드러낸다. 조용히 삼키면 원인 추적이 불가능해진다
                    sendGAEvent('signup_db_failed', {
                        method: provider || 'unknown',
                        status: result.status,
                        reason: result.reason || 'unknown',
                        has_token: token ? 'yes' : 'no'
                    })
                }

                // 등록에 성공한 '진짜 신규 계정'에만 축하 모달을 띄운다.
                // 닉네임이 비어 뒤늦게 채워진 기존 회원에게는 띄우지 않는다.
                if (registered && isBrandNewAccount) sessionStorage.setItem('showSignupComplete', 'true')
            }

            const returnUrl = sessionStorage.getItem('returnUrl')
            sessionStorage.removeItem('returnUrl')

            if (isBrandNewAccount && registered) {
                // 신규 가입 이벤트 전송 완료 후 리다이렉트 (즉시 이동 시 이벤트 유실 방지)
                sendGAEventAndRedirect('sign_up', { method: provider || 'unknown' }, returnUrl || '/')
            } else {
                window.location.replace(returnUrl || '/')
            }
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
