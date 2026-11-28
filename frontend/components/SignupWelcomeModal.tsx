'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronDown, MapPin } from 'lucide-react'
import { supabase } from '@/lib/supabase'
import { sendGAEvent } from '@/lib/analytics'
import { useLibrary } from '@/context/LibraryContext'
import { useAuth } from '@/context/AuthContext'
import LibrarySelector from '@/components/LibrarySelector'

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

const AGE_OPTIONS = [
    { key: '0-3', label: '0~3세' },
    { key: '4-7', label: '4~7세' },
    { key: '8-12', label: '8~12세' },
    { key: '13+', label: '13세 이상' },
] as const

function generateRandomNickname() {
    const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]
    const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)]
    return `${adj}${noun}`
}

export default function SignupWelcomeModal() {
    const [isOpen, setIsOpen] = useState(false)
    const [nickname, setNickname] = useState('')
    const [isUserEdited, setIsUserEdited] = useState(false)
    const [isDuplicate, setIsDuplicate] = useState(false)
    const [isCheckingDuplicate, setIsCheckingDuplicate] = useState(false)
    const [selectedAge, setSelectedAge] = useState<string>('')
    const [isSaving, setIsSaving] = useState(false)
    const router = useRouter()
    const { selectedLibrary } = useLibrary()
    const { preferredChildAge, updatePreferredChildAge } = useAuth()

    useEffect(() => {
        if (typeof window === 'undefined') return
        if (sessionStorage.getItem('showSignupComplete') === 'true') {
            sessionStorage.removeItem('showSignupComplete')
            const signupMethod = sessionStorage.getItem('pendingSignupMethod') || localStorage.getItem('last_login_provider') || 'unknown'
            sessionStorage.removeItem('pendingSignupMethod')
            sendGAEvent('sign_up', { method: signupMethod })

            if (preferredChildAge) setSelectedAge(preferredChildAge)

            const loadInitialNickname = async () => {
                const savedNickname = sessionStorage.getItem('generatedNickname')
                sessionStorage.removeItem('generatedNickname')
                if (savedNickname) {
                    setNickname(savedNickname)
                    setIsOpen(true)
                    return
                }
                try {
                    const { data: { user } } = await supabase.auth.getUser()
                    if (user) {
                        const { data } = await supabase.from('members').select('nickname').eq('id', user.id).single()
                        if (data?.nickname) {
                            setNickname(data.nickname)
                            setIsOpen(true)
                            return
                        }
                    }
                } catch { /* ignore */ }
                setNickname(generateRandomNickname())
                setIsOpen(true)
            }
            loadInitialNickname()
        }
    }, [])

    const nicknameValidation = useMemo(() => {
        const trimmed = nickname.trim()
        return {
            isLengthValid: trimmed.length >= 2 && trimmed.length <= 10,
            isFormatValid: /^[가-힣a-zA-Z0-9]+$/.test(trimmed)
        }
    }, [nickname])

    const isNicknameValid = nicknameValidation.isLengthValid && nicknameValidation.isFormatValid

    // 실시간 닉네임 중복 검사 (디바운스 300ms)
    useEffect(() => {
        const trimmed = nickname.trim()
        if (!trimmed || !nicknameValidation.isLengthValid || !nicknameValidation.isFormatValid) {
            setIsDuplicate(false)
            setIsCheckingDuplicate(false)
            return
        }

        let isCancelled = false
        setIsCheckingDuplicate(true)

        const timer = setTimeout(async () => {
            try {
                const isLocal = typeof window !== 'undefined' && (
                    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                )
                const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (isLocal ? 'http://127.0.0.1:8000' : 'https://api.checkjari.com')

                const { data: sessionData } = await supabase.auth.getSession()
                const token = sessionData?.session?.access_token || ''

                const res = await fetch(`${API_BASE_URL}/api/auth/check-nickname?nickname=${encodeURIComponent(trimmed)}`, {
                    headers: token ? { Authorization: `Bearer ${token}` } : {}
                })
                if (res.ok) {
                    const data = await res.json()
                    if (!isCancelled) {
                        setIsDuplicate(!data.available)
                    }
                }
            } catch {
                // 네트워크 오류 시 조용히 통과
            } finally {
                if (!isCancelled) {
                    setIsCheckingDuplicate(false)
                }
            }
        }, 300)

        return () => {
            isCancelled = true
            clearTimeout(timer)
        }
    }, [nickname, nicknameValidation])

    const handleSave = async () => {
        if (!isNicknameValid || isDuplicate || isCheckingDuplicate || isSaving) return
        setIsSaving(true)

        try {
            if (selectedLibrary) {
                if (sessionStorage.getItem('pendingAction') === 'open_library_selector') {
                    sessionStorage.removeItem('pendingAction')
                    sessionStorage.removeItem('returnUrl')
                }
            }

            sendGAEvent('complete_onboarding', {
                has_age: !!selectedAge,
                has_library: !!selectedLibrary,
                age: selectedAge || 'none',
                library: selectedLibrary || 'none',
            })

            const isQaMode = localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN'

            if (isQaMode) {
                // QA 모드: 실제 API 호출 없이 sessionStorage에만 저장
                sessionStorage.setItem('qa_saved_nickname', nickname.trim())
                await updatePreferredChildAge(selectedAge || null)
            } else {
                const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                const API_BASE_URL = isLocal
                    ? 'http://127.0.0.1:8000'
                    : (process.env.NEXT_PUBLIC_API_URL || 'https://api.checkjari.com')

                const { data: sessionData } = await supabase.auth.getSession()
                const token = sessionData?.session?.access_token || ''

                const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        nickname: nickname.trim(),
                        preferred_child_age: selectedAge || null,
                    })
                })
                if (res.status === 409) {
                    setIsDuplicate(true)
                    return
                }
                if (!res.ok) throw new Error(`Nickname save failed: ${res.status}`)
                await updatePreferredChildAge(selectedAge || null)
            }
            setIsOpen(false)
            if (
                typeof window !== 'undefined' &&
                (window.location.pathname.startsWith('/auth') ||
                    window.location.pathname === '/login' ||
                    window.location.pathname === '/signup')
            ) {
                router.push('/')
            }
        } catch (e) {
            console.error('Nickname save failed:', e)
        } finally {
            setIsSaving(false)
        }
    }

    const handleClose = () => setIsOpen(false)

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-6 bg-black/40 backdrop-blur-[1px]">
            <div className="relative w-full max-w-[360px] bg-white rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.12)]">
                {/* 닫기 버튼 */}
                <button
                    onClick={handleClose}
                    className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center text-gray-400 active:text-gray-600 transition-colors outline-none focus:outline-none"
                    aria-label="닫기"
                >
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                        <path d="M2 2L16 16M16 2L2 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                </button>

                {/* 헤더 */}
                <div className="mb-5">
                    <p className="text-[13px] text-amber-600 font-bold mb-1">책자리에 오신 걸 환영해요</p>
                    <h2 className="text-[20px] font-bold text-gray-900 leading-snug">
                        우리 아이 맞춤 책장을 준비할게요
                    </h2>
                </div>

                {/* 1. 닉네임 입력 (필수) */}
                <div className="mb-4">
                    <label className="block text-[13px] font-bold text-gray-700 mb-1.5">
                        닉네임<span className="text-red-500 ml-0.5">*</span>
                    </label>
                    <input
                        type="text"
                        value={nickname}
                        onChange={(e) => {
                            setNickname(e.target.value.replace(/\s/g, ''))
                            setIsUserEdited(true)
                            setIsDuplicate(false)
                        }}
                        maxLength={10}
                        autoFocus
                        className={`w-full h-[46px] px-4 bg-gray-50 border rounded-xl focus:outline-none transition-all text-[15px] text-gray-900 ${isDuplicate
                                ? 'border-red-400 focus:border-red-500 focus:bg-white'
                                : 'border-gray-200 focus:border-brand-primary focus:bg-white'
                            }`}
                        placeholder="2~10자, 한글·영문·숫자"
                    />
                    <p className={`text-[12px] px-1 mt-1.5 h-4 leading-4 ${nickname.length === 0 || (!isUserEdited && !isDuplicate) ? 'text-transparent' :
                            !nicknameValidation.isFormatValid || !nicknameValidation.isLengthValid || isDuplicate ? 'text-red-500 font-medium' :
                                'text-[#10B981] font-medium'
                        }`}>
                        {!nicknameValidation.isFormatValid ? '특수문자나 공백은 사용할 수 없어요' :
                            !nicknameValidation.isLengthValid ? '2자 이상 10자 이하로 입력해주세요' :
                                isCheckingDuplicate ? '중복 확인 중...' :
                                    isDuplicate ? '이미 사용 중인 닉네임이에요' :
                                        isUserEdited ? '사용 가능한 닉네임이에요' : ''}
                    </p>
                </div>

                {/* 2. 우리 아이 연령대 */}
                <div className="mb-4">
                    <label className="block text-[13px] font-bold text-gray-700 mb-1.5">
                        우리 아이 연령대
                    </label>
                    <div className="grid grid-cols-4 gap-1.5">
                        {AGE_OPTIONS.map((opt) => {
                            const isSelected = selectedAge === opt.key
                            return (
                                <button
                                    key={opt.key}
                                    type="button"
                                    onClick={() => setSelectedAge(isSelected ? '' : opt.key)}
                                    className={`h-10 rounded-xl text-xs transition-all outline-none focus:outline-none ${isSelected
                                            ? 'bg-brand-primary text-white font-bold shadow-xs active:bg-brand-primary-dark'
                                            : 'bg-white text-gray-700 font-medium border border-gray-200/80 active:bg-gray-100'
                                        }`}
                                >
                                    {opt.label}
                                </button>
                            )
                        })}
                    </div>
                </div>

                {/* 3. 자주 가는 도서관 (전국 1,600+ 공공도서관 공용 선택기) */}
                <div className="mb-5">
                    <label className="block text-[13px] font-bold text-gray-700 mb-1.5">
                        자주 가는 도서관
                    </label>
                    <LibrarySelector
                        customTrigger={(open) => (
                            <button
                                type="button"
                                onClick={open}
                                className="w-full h-[46px] px-4 bg-gray-50 border border-gray-200 rounded-xl flex items-center justify-between gap-2 text-left active:bg-gray-100 transition-all outline-none focus:outline-none focus:border-brand-primary"
                            >
                                <span className="flex items-center gap-2 min-w-0">
                                    <MapPin className={`w-4 h-4 shrink-0 ${selectedLibrary ? 'text-amber-500' : 'text-gray-400'}`} />
                                    <span className={`text-[14px] truncate ${selectedLibrary ? 'text-gray-900 font-semibold' : 'text-gray-400'}`}>
                                        {selectedLibrary || '우리 동네 도서관 검색하기 (선택)'}
                                    </span>
                                </span>
                                <ChevronDown className="w-4 h-4 text-gray-400 shrink-0" />
                            </button>
                        )}
                    />
                </div>

                {/* 하단 버튼 */}
                <div>
                    <button
                        onClick={handleSave}
                        disabled={!isNicknameValid || isDuplicate || isCheckingDuplicate || isSaving}
                        className={`w-full h-[50px] rounded-xl text-[16px] font-bold transition-all active:scale-[0.98] outline-none focus:outline-none
                            ${isNicknameValid && !isDuplicate && !isCheckingDuplicate && !isSaving
                                ? 'bg-brand-primary text-white active:bg-brand-primary-dark'
                                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            }`}
                    >
                        {isSaving ? '저장 중...' : '맞춤 책장 시작하기'}
                    </button>
                </div>
            </div>
        </div>
    )
}
