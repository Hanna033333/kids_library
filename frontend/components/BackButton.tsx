'use client'

import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ChevronLeft } from 'lucide-react'

interface BackButtonProps {
    onClick?: () => void
    href?: string
    className?: string
}

export default function BackButton({ onClick, href, className = '' }: BackButtonProps) {
    const router = useRouter()

    const baseClass = `flex items-center justify-center w-10 h-10 -ml-2 text-gray-500 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100 ${className}`

    const handleBack = (e: React.MouseEvent) => {
        if (onClick) {
            e.preventDefault()
            onClick()
            return
        }

        // 세션스토리지에 저장된 내부 경로 이동 기록을 활용하여 이전 페이지가 동일 서비스인지 확인
        if (typeof window !== 'undefined') {
            try {
                const stored = sessionStorage.getItem('checkjari_history')
                const historyStack: string[] = stored ? JSON.parse(stored) : []
                
                // historyStack의 길이가 1보다 크면 세션 내에서 내부 페이지 이동 히스토리가 존재함을 의미합니다.
                if (historyStack.length > 1) {
                    e.preventDefault()
                    router.back()
                } else {
                    e.preventDefault()
                    router.push(href || '/')
                }
            } catch (err) {
                // sessionStorage 접근이 차단되거나 오류 발생 시 폴백 처리
                const referrer = document.referrer
                const isInternalReferrer = referrer && referrer.includes(window.location.host)
                
                if (isInternalReferrer) {
                    e.preventDefault()
                    router.back()
                } else {
                    e.preventDefault()
                    router.push(href || '/')
                }
            }
        } else {
            e.preventDefault()
            router.push(href || '/')
        }
    }

    return (
        <button
            onClick={handleBack}
            className={baseClass}
            aria-label="뒤로가기"
        >
            <ChevronLeft className="w-6 h-6" />
        </button>
    )
}
