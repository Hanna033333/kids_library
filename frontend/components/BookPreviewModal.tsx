'use client'

import { useState, useEffect } from 'react'
import { X, ChevronLeft, ChevronRight, BookOpen } from 'lucide-react'
import Image from 'next/image'
import { getOptimizedImageUrl } from '@/lib/utils/image'

interface BookPreviewModalProps {
    isOpen: boolean
    onClose: () => void
    bookTitle: string
    coverUrl?: string | null
    previewUrls?: string[] | null
}

export default function BookPreviewModal({
    isOpen,
    onClose,
    bookTitle,
    coverUrl,
    previewUrls
}: BookPreviewModalProps) {
    const [currentIndex, setCurrentIndex] = useState(0)

    // 모달이 열릴 때 스크롤 락 및 인덱스 초기화
    useEffect(() => {
        if (isOpen) {
            setCurrentIndex(0)
            document.body.style.overflow = 'hidden'
        } else {
            document.body.style.overflow = 'unset'
        }
        return () => {
            document.body.style.overflow = 'unset'
        }
    }, [isOpen])

    if (!isOpen) return null

    const images = previewUrls || []
    const hasMultiple = images.length > 1

    const handlePrev = () => {
        setCurrentIndex((prev) => (prev > 0 ? prev - 1 : images.length - 1))
    }

    const handleNext = () => {
        setCurrentIndex((prev) => (prev < images.length - 1 ? prev + 1 : 0))
    }

    return (
        <div 
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-200"
            onClick={onClose}
        >
            <div 
                className="relative w-full max-w-2xl h-[85dvh] mx-4 bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Modal Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 shrink-0">
                    <div className="flex items-center gap-2 min-w-0 pr-4">
                        <BookOpen className="w-5 h-5 text-amber-500 shrink-0" />
                        <h3 className="font-bold text-base md:text-lg text-gray-900 truncate">
                            {bookTitle} 미리보기
                        </h3>
                    </div>
                    {/* Counter Pill Badge */}
                    {images.length > 0 && (
                        <div className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-bold shrink-0 mr-2">
                            {currentIndex + 1} / {images.length}
                        </div>
                    )}
                    {/* Close Button (Minimum 48x48 touch target) */}
                    <button
                        onClick={onClose}
                        className="w-12 h-12 flex items-center justify-center text-gray-400 active:text-gray-900 active:bg-gray-100 rounded-full transition-colors shrink-0 -mr-2"
                        aria-label="닫기"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Content Body */}
                <div className="relative flex-1 bg-gray-50 flex items-center justify-center p-4 overflow-hidden">
                    {images.length > 0 ? (
                        <div className="relative w-full h-full flex items-center justify-center">
                            <Image
                                src={getOptimizedImageUrl(images[currentIndex], 'detail')}
                                alt={`${bookTitle} 미리보기 ${currentIndex + 1}`}
                                fill
                                priority
                                className="object-contain transition-all duration-300"
                                sizes="(max-width: 768px) 100vw, 600px"
                            />
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center text-gray-400 gap-3">
                            <BookOpen className="w-16 h-16 opacity-30" />
                            <p className="text-sm font-semibold">등록된 미리보기 이미지가 없습니다.</p>
                        </div>
                    )}

                    {/* Navigation Buttons for multiple images */}
                    {hasMultiple && (
                        <>
                            <button
                                onClick={handlePrev}
                                className="absolute left-3 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/90 shadow-md text-gray-800 rounded-full flex items-center justify-center active:scale-95 transition-transform"
                                aria-label="이전 이미지"
                            >
                                <ChevronLeft className="w-6 h-6" />
                            </button>
                            <button
                                onClick={handleNext}
                                className="absolute right-3 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/90 shadow-md text-gray-800 rounded-full flex items-center justify-center active:scale-95 transition-transform"
                                aria-label="다음 이미지"
                            >
                                <ChevronRight className="w-6 h-6" />
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}
