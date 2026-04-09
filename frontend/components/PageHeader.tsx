import React from 'react'
import BackButton from '@/components/BackButton'

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
}: PageHeaderProps) {
    const left =
        leftSlot !== undefined ? (
            leftSlot
        ) : (
            <BackButton href={backHref} onClick={backOnClick} />
        )

    return (
        <header className="w-full bg-white border-b border-gray-100 flex items-center justify-between px-6 py-4 sticky top-0 z-50">
            <div className="w-1/3 flex items-center">{left}</div>
            <div className="w-1/3 flex justify-center">
                <h1 className="text-lg font-bold text-gray-900 truncate">{title}</h1>
            </div>
            <div className="w-1/3 flex justify-end">{rightSlot ?? null}</div>
        </header>
    )
}
