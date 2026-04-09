'use client'

import { X } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface CloseButtonProps {
    className?: string
}

export default function CloseButton({ className = '' }: CloseButtonProps) {
    const router = useRouter()

    const handleClose = () => {
        // 우선 창 닫기 시도
        window.close()
        
        // 0.1초 후에도 창이 닫히지 않았다면 (새 창이 아닌 경우 등) 뒤로가기 실행
        setTimeout(() => {
            router.back()
        }, 100)
    }

    return (
        <button
            onClick={handleClose}
            className={`flex items-center justify-center w-10 h-10 -mr-2 text-gray-500 transition-transform active:scale-95 ${className}`}
            aria-label="닫기"
        >
            <X className="w-6 h-6" />
        </button>
    )
}
