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

    if (href) {
        return (
            <Link href={href} className={baseClass} aria-label="뒤로가기">
                <ChevronLeft className="w-6 h-6" />
            </Link>
        )
    }

    return (
        <button
            onClick={onClick || (() => router.back())}
            className={baseClass}
            aria-label="뒤로가기"
        >
            <ChevronLeft className="w-6 h-6" />
        </button>
    )
}
