'use client'

import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import { type Book } from '@/lib/types'
import { PageLoader } from '@/components/ui/PageLoader'
import BookCard from './BookCard'

interface CurationSectionProps {
  subtitle: string
  title: string
  books: Book[]
  href: string
  onViewMore: () => void
  bgColor?: string
  minBooks?: number
}

/**
 * 홈 화면 큐레이션 섹션 컴포넌트
 * 
 * 2단 타이틀(서브타이틀 + 메인타이틀) + 좌우 스크롤 책 카드 로울 구성입니다.
 * minBooks 미만이면 섹션 자체를 숨겨 빈칸 노출을 방지합니다.
 */
export default function CurationSection({
  subtitle,
  title,
  books,
  href,
  onViewMore,
  bgColor = 'bg-muted-bg',
  minBooks = 7,
}: CurationSectionProps) {
  // 지정된 권수 미만인 경우 섹션 자체를 노출하지 않음 (유저 경험 보장)
  if (books.length < minBooks) return null

  return (
    <section className={`py-8 px-4 ${bgColor}`}>
      <div className="max-w-[1200px] mx-auto">
        <div className="flex items-end justify-between mb-8 px-2">
          <div className="flex flex-col gap-1">
            <span className="text-[13px] font-semibold text-gray-500 tracking-tight">
              {subtitle}
            </span>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight leading-tight">
              {title}
            </h2>
          </div>
          <Link
            href={href}
            className="text-gray-900 p-1 mb-0.5"
            onClick={onViewMore}
          >
            <ChevronRight className="w-6 h-6" />
          </Link>
        </div>

        {books.length > 0 ? (
          <div className="overflow-x-auto scrollbar-hide -mx-4 px-6">
            <div className="flex gap-4 pb-4">
              {books.map((book, index) => (
                <div key={book.id} className={`flex-shrink-0 w-[165px] sm:w-[190px] ${index === books.length - 1 ? 'mr-4' : ''}`}>
                  <BookCard book={book} />
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="h-[280px] flex items-center justify-center mx-2">
            <PageLoader />
          </div>
        )}
      </div>
    </section>
  )
}
