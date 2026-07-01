'use client'

import Link from 'next/link'
import Image from 'next/image'
import { BookOpen } from 'lucide-react'
import { type Book } from '@/lib/types'
import { getAgeDisplayLabel } from '@/lib/utils/age'
import { sendGAEvent } from '@/lib/analytics'
import { getOptimizedImageUrl } from '@/lib/utils/image'

/**
 * 홈 화면 전용 책 카드 컴포넌트
 * 
 * 도서 정보를 표지 이미지 + 제목 + 출판사 구성의 카드 UI로 표시합니다.
 * 청구기호, 도서관 소장 정보 등은 홈 화면에서 노출하지 않아 비주얼을 깔끔하게 유지합니다.
 */
export default function BookCard({ book }: { book: Book }) {
  const displayAge = getAgeDisplayLabel(book.age)

  return (
    <Link
      href={`/book/${book.id}`}
      onClick={() => sendGAEvent('click_book_item', { book_id: book.id, book_title: book.title })}
      className="flex flex-col bg-white rounded-2xl shadow-sm overflow-hidden transition-all h-full group active:scale-[0.98]"
    >
      {/* 1. 이미지 영역 (상단) */}
      <div className="relative w-full aspect-[1/1.1] bg-[#F9FAFB] overflow-hidden flex items-center justify-center">
        {book.image_url ? (
          <Image
            src={getOptimizedImageUrl(book.image_url, 'list')}
            alt={book.title}
            fill
            sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="w-full h-full object-cover transition-transform duration-300 group-active:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="flex flex-col items-center justify-center w-full h-full text-gray-300">
            <BookOpen className="w-12 h-12 opacity-20" />
          </div>
        )}

        {/* 태그 (이미지 위에 오버레이) */}
        <div className="absolute top-3 left-3 flex gap-1.5 flex-wrap">
          {book.category && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/90 text-gray-600 font-bold shadow-sm backdrop-blur-sm">
              {book.category}
            </span>
          )}
          {displayAge && (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-black/60 text-white font-medium shadow-sm backdrop-blur-sm">
              {displayAge}
            </span>
          )}
        </div>
      </div>

      {/* 2. 정보 영역 (하단) */}
      <div className="flex-1 p-4 flex flex-col items-start bg-white">
        <h3 className="text-base font-bold text-gray-900 leading-[1.35] mb-1.5 line-clamp-2 tracking-tight">
          {book.title}
        </h3>

        <div className="mt-auto pt-3 border-t border-gray-50 w-full flex items-center justify-between text-xs font-medium">
          <span className="text-gray-400 truncate max-w-[60%]">{book.publisher}</span>
        </div>
      </div>
    </Link>
  )
}
