'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

const ADJECTIVES = ['지혜로운', '따스한', '포근한', '정겨운', '행복한', '다정한', '꿈꾸는', '다독이는', '슬기로운', '다복한', '마음넓은', '빛나는']
const NOUNS = ['책벌레', '이야기꾼', '책부엉이', '파랑새', '독서가', '책요정', '글벗', '책탐험가', '책마을님']

function generateRandomNickname() {
    const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]
    const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)]
    return `${adj}${noun}`
}

export default function SignupWelcomeModal() {
    const [isOpen, setIsOpen] = useState(false)
    const [nickname, setNickname] = useState('')
    const [isSaving, setIsSaving] = useState(false)
    const router = useRouter()

    useEffect(() => {
        if (typeof window === 'undefined') return
        if (sessionStorage.getItem('showSignupComplete') === 'true') {
            sessionStorage.removeItem('showSignupComplete')
            // 콜백에서 생성된 랜덤 닉네임 복원, 없으면 새로 생성
            const savedNickname = sessionStorage.getItem('generatedNickname') || generateRandomNickname()
            sessionStorage.removeItem('generatedNickname')
            setNickname(savedNickname)
            setIsOpen(true)
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

    const handleSave = async () => {
        if (!isNicknameValid || isSaving) return
        setIsSaving(true)

        try {
            const isQaMode = localStorage.getItem('supabase.auth.token') === 'TEST_QA_TOKEN'

            if (isQaMode) {
                // QA 모드: 실제 API 호출 없이 sessionStorage에만 저장
                sessionStorage.setItem('qa_saved_nickname', nickname.trim())
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
                    body: JSON.stringify({ nickname: nickname.trim() })
                })
                if (!res.ok) throw new Error(`Nickname save failed: ${res.status}`)
            }
        } catch (e) {
            console.error('Nickname save failed:', e)
        } finally {
            setIsSaving(false)
            setIsOpen(false)
            router.push('/')
        }
    }

    const handleClose = () => setIsOpen(false)

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-6">
            {/* 딤 배경 없음 (기존 스타일 유지) */}
            <div className="relative w-full max-w-[340px] bg-white rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.12)]">
                {/* 닫기 버튼 */}
                <button
                    onClick={handleClose}
                    className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center text-gray-400 active:text-gray-600 transition-colors"
                    aria-label="닫기"
                >
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                        <path d="M2 2L16 16M16 2L2 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                </button>

                {/* 헤더 */}
                <div className="mb-5">
                    <p className="text-[13px] text-gray-400 font-medium mb-1">책자리에 오신 걸 환영해요</p>
                    <h2 className="text-[20px] font-bold text-gray-900 leading-snug">
                        닉네임을 정해주세요
                    </h2>
                </div>

                {/* 닉네임 입력 */}
                <div className="mb-2">
                    <input
                        type="text"
                        value={nickname}
                        onChange={(e) => setNickname(e.target.value.replace(/\s/g, ''))}
                        maxLength={10}
                        autoFocus
                        className="w-full h-[50px] px-4 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:border-gray-900 focus:bg-white transition-all text-[16px] text-gray-900"
                        placeholder="2~10자, 한글·영문·숫자"
                    />
                    <p className="mt-2 text-[12px] text-gray-400 px-1">
                        언제든지 마이페이지에서 변경할 수 있어요
                    </p>
                </div>

                {/* 하단 버튼 */}
                <div className="mt-5 space-y-2">
                    <button
                        onClick={handleSave}
                        disabled={!isNicknameValid || isSaving}
                        className={`w-full h-[50px] rounded-xl text-[16px] font-bold transition-all active:scale-[0.98]
                            ${isNicknameValid && !isSaving
                                ? 'bg-[#F59E0B] text-white active:bg-[#D97706]'
                                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            }`}
                    >
                        {isSaving ? '저장 중...' : '시작하기'}
                    </button>
                    <button
                        onClick={handleClose}
                        className="w-full h-[44px] rounded-xl text-[14px] font-medium text-gray-400 active:text-gray-600 transition-colors"
                    >
                        나중에 설정할게요
                    </button>
                </div>
            </div>
        </div>
    )
}
