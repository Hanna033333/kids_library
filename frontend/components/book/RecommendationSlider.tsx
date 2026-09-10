'use client'

import { ReactNode } from 'react'
import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import BookCard from '@/components/home/BookCard'
import { Book } from '@/lib/types'

interface RecommendationSliderProps {
    /** 노출할 추천 도서 목록. 비어 있으면 섹션 자체를 렌더링하지 않는다. */
    books: Book[]
    /** 2단 타이틀의 상단 서브 타이틀 (design.md 섹션 타이틀 구조) */
    subtitle: string
    /** 2단 타이틀의 하단 메인 타이틀. `[추천그룹] 책 추천 리스트` 포맷으로 통일한다. */
    title: ReactNode
    /** 우측 더보기(>) 링크. 없으면 더보기 버튼을 숨긴다. */
    href?: string
    /** React key 접두사 (한 페이지에 여러 섹션이 같은 도서를 노출할 수 있으므로 필요) */
    keyPrefix: string
    /** 래퍼의 배경/여백 클래스. 섹션 간 교차 배경(회색 ↔ 흰색) 적용에 사용한다. */
    className?: string
}

/**
 * 도서 상세 페이지 하단의 추천 도서 가로 슬라이더.
 *
 * design.md '도서 상세 페이지 추천 영역' 규격을 단일 지점에서 보장한다.
 * - 상단 패딩 `pt-8`로 섹션 간 타이틀 시작 높이 정렬
 * - 래퍼에 `w-full px-6`로 모바일 좌우 24px 패딩 유지,
 *   스크롤 컨테이너에만 `-mx-6 px-6`을 적용해 카드가 화면 양끝으로 흐르게 한다
 * - 카드 너비는 홈 큐레이션과 1:1로 일치하는 `w-[165px] sm:w-[190px]`
 */
export default function RecommendationSlider({
    books,
    subtitle,
    title,
    href,
    keyPrefix,
    className = 'bg-white pt-8 pb-10 w-full px-6',
}: RecommendationSliderProps) {
    if (!books || books.length === 0) return null

    return (
        <div className={className}>
            <div className="max-w-4xl mx-auto">
                <div className="flex items-end justify-between mb-6 px-2">
                    <div className="flex flex-col gap-0.5">
                        <span className="text-[12px] font-bold text-gray-500 tracking-tight">
                            {subtitle}
                        </span>
                        <h3 className="text-lg sm:text-xl font-black text-gray-900 tracking-tight leading-tight">
                            {title}
                        </h3>
                    </div>
                    {href && (
                        <Link
                            href={href}
                            className="text-gray-950 p-1 mb-0.5"
                            aria-label="더보기"
                        >
                            <ChevronRight className="w-6 h-6" />
                        </Link>
                    )}
                </div>
                <div className="overflow-x-auto scrollbar-hide -mx-6 px-6">
                    <div className="flex gap-4 pb-2">
                        {books.map((b) => (
                            <div key={`${keyPrefix}-${b.id}`} className="flex-shrink-0 w-[165px] sm:w-[190px]">
                                <BookCard book={b} />
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}
