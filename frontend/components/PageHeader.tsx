import React from 'react'
import BackButton from '@/components/BackButton'
import Link from 'next/link'
import { Home } from 'lucide-react'

interface PageHeaderProps {
    title: string
    /** 왼쪽 슬롯 (기본: BackButton) */
    leftSlot?: React.ReactNode
    /** 오른쪽 슬롯 (기본: 빈 공간) */
    rightSlot?: React.ReactNode
    /** BackButton의 href (leftSlot을 따로 지정하지 않을 때 사용) */
    backHref?: string
    /** BackButton의 onClick (leftSlot을 따로 지정하지 않을 때 사용) */
    backOnClick?: () => void
    /** 백버튼 옆 홈 버튼 노출 여부 */
    showHome?: boolean
}

/**
 * 공통 페이지 상단 헤더 컴포넌트
 * - sticky top-0, 좌/중앙/우 3분할 레이아웃
 * - 타이틀은 이모티콘 없이 텍스트만
 */
export default function PageHeader({
    title,
    leftSlot,
    rightSlot,
    backHref,
    backOnClick,
    showHome = false,
}: PageHeaderProps) {
    const left =
        leftSlot !== undefined ? (
            leftSlot
        ) : (
            <div className="flex items-center">
                <BackButton href={backHref} onClick={backOnClick} />
                {showHome && (
                    <Link
                        href="/"
                        className="flex items-center justify-center w-10 h-10 text-gray-500 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100 active:scale-95"
                        aria-label="홈으로 이동"
                    >
                        <Home className="w-5 h-5" />
                    </Link>
                )}
            </div>
        )

    return (
        <header className="w-full bg-white border-b border-gray-100 flex items-center justify-between px-6 py-4 sticky top-0 z-50">
            <div className="w-[84px] flex-shrink-0 flex items-center">{left}</div>
            <div className="flex-1 min-w-0 mx-2 flex justify-center">
                <h1 className="text-lg font-bold text-gray-900 truncate">{title}</h1>
            </div>
            <div className="w-[84px] flex-shrink-0 flex items-center justify-end">{rightSlot ?? null}</div>
        </header>
    )
}
