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

        // 브라우저 document.referrer를 활용하여 이전 페이지가 동일 서비스인지 확인
        if (typeof window !== 'undefined') {
            const referrer = document.referrer
            const isInternalReferrer = referrer && referrer.includes(window.location.host)
            
            if (isInternalReferrer) {
                e.preventDefault()
                router.back()
            } else {
                // 이전 페이지가 없거나 외부(네이버 등)인 경우 지정된 href 또는 홈으로 리다이렉트
                e.preventDefault()
                router.push(href || '/')
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
