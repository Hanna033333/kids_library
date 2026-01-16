'use client'

import { useState, useRef, useEffect } from 'react'
import { useLibrary, LibraryName } from '@/context/LibraryContext'
import { ChevronDown, MapPin, Check } from 'lucide-react'
import { createPortal } from 'react-dom'

export default function LibrarySelector({ whiteMode = false }: { whiteMode?: boolean }) {
    const { selectedLibrary, setSelectedLibrary, availableLibraries } = useLibrary()
    const [isOpen, setIsOpen] = useState(false)
    const [isAnimating, setIsAnimating] = useState(false)

    // 바텀 시트 열기/닫기 애니메이션 처리
    useEffect(() => {
        if (isOpen) {
            setIsAnimating(true)
            document.body.style.overflow = 'hidden' // 스크롤 방지
        } else {
            const timer = setTimeout(() => setIsAnimating(false), 300) // 애니메이션 시간 대기
            document.body.style.overflow = ''
            return () => clearTimeout(timer)
        }
    }, [isOpen])

    const handleSelect = (lib: string) => {
        setSelectedLibrary(lib as LibraryName)
        setIsOpen(false)
    }

    return (
        <>
            {/* Trigger Button */}
            <button
                onClick={() => setIsOpen(true)}
                className={`flex items-center gap-1.5 text-sm font-bold border-b-2 pb-0.5 transition-colors ${whiteMode
                    ? 'text-white border-white/40 hover:border-white'
                    : 'text-gray-900 border-gray-900/10 hover:border-gray-900'
                    }`}
            >
                <MapPin className="w-3.5 h-3.5" />
                <span>{selectedLibrary}</span>
                <ChevronDown className="w-3.5 h-3.5 opacity-50" />
            </button>

            {/* Bottom Sheet Portal */}
            {(isOpen || isAnimating) && createPortal(
                <div className={`fixed inset-0 z-[100] flex justify-center items-end sm:items-center pointer-events-none`}>
                    {/* Overlay */}
                    <div
                        className={`absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity duration-300 pointer-events-auto ${isOpen ? 'opacity-100' : 'opacity-0'}`}
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Sheet */}
                    <div
                        className={`w-full max-w-md bg-white rounded-t-[28px] sm:rounded-[28px] shadow-2xl overflow-hidden pointer-events-auto transition-transform duration-300 transform ${isOpen ? 'translate-y-0 scale-100' : 'translate-y-full sm:translate-y-8 sm:scale-95'
                            } safe-area-bottom`}
                    >
                        <div className="p-6 pb-8">
                            <div className="flex justify-center mb-6">
                                <div className="w-12 h-1.5 bg-gray-200 rounded-full" />
                            </div>

                            <h3 className="text-xl font-bold text-gray-900 mb-2 px-1">
                                도서관을 선택해주세요
                            </h3>
                            <p className="text-gray-500 text-sm mb-6 px-1">
                                선택한 도서관의 청구기호를 우선적으로 보여드립니다.
                            </p>

                            <div className="space-y-2">
                                {availableLibraries.map((lib) => (
                                    <button
                                        key={lib}
                                        onClick={() => handleSelect(lib)}
                                        className={`w-full flex items-center justify-between p-4 rounded-xl text-left transition-all ${selectedLibrary === lib
                                            ? 'bg-[#F59E0B]/10 text-[#F59E0B] font-bold border border-[#F59E0B]/20'
                                            : 'bg-gray-50 text-gray-700 font-medium hover:bg-gray-100 border border-transparent'
                                            }`}
                                    >
                                        <span className="flex items-center gap-3">
                                            <span className={`w-2 h-2 rounded-full ${selectedLibrary === lib ? 'bg-[#F59E0B]' : 'bg-gray-300'}`} />
                                            {lib}
                                        </span>
                                        {selectedLibrary === lib && (
                                            <Check className="w-5 h-5" />
                                        )}
                                    </button>
                                ))}
                            </div>

                            <button
                                onClick={() => setIsOpen(false)}
                                className="w-full mt-6 py-3.5 rounded-xl text-gray-500 font-medium hover:bg-gray-50 transition-colors"
                            >
                                닫기
                            </button>
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </>
    )
}
