'use client'

import { useState, useRef, useEffect } from 'react'
import { useLibrary, LibraryName } from '@/context/LibraryContext'
import { ChevronDown, MapPin, Check, X } from 'lucide-react'
import { createPortal } from 'react-dom'

export default function LibrarySelector({ 
    whiteMode = false, 
    autoOpen = false,
    customTrigger
}: { 
    whiteMode?: boolean
    autoOpen?: boolean 
    customTrigger?: (open: () => void) => React.ReactNode
}) {
    const { selectedLibrary, setSelectedLibrary, availableLibraries } = useLibrary()
    const [isOpen, setIsOpen] = useState(autoOpen)
    const [isAnimating, setIsAnimating] = useState(false)

    // autoOpen 프로퍼티가 변경되거나 true로 들어올 때 열림 처리
    useEffect(() => {
        if (autoOpen) {
            setIsOpen(true)
        }
    }, [autoOpen])

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

    const displayLibraryName = selectedLibrary
        ? (selectedLibrary.length > 15 ? `${selectedLibrary.slice(0, 15)}...` : selectedLibrary)
        : '도서관을 선택해주세요'

    return (
        <>
            {/* Trigger Button */}
            {customTrigger ? (
                customTrigger(() => setIsOpen(true))
            ) : (
                <button
                    onClick={() => setIsOpen(true)}
                    className={`flex items-center gap-1.5 text-sm sm:text-base font-bold py-1 px-0.5 transition-colors shrink-0 max-w-full ${whiteMode
                        ? 'text-white hover:text-white/80'
                        : selectedLibrary 
                            ? 'text-gray-900 hover:text-gray-700 font-black' 
                            : 'text-gray-400 hover:text-gray-600 font-medium'
                        }`}
                >
                    <MapPin className={`w-4 h-4 shrink-0 ${whiteMode ? 'text-white' : selectedLibrary ? 'text-amber-500' : 'text-gray-400'}`} />
                    <span className="truncate underline decoration-gray-300 underline-offset-4">
                        {displayLibraryName}
                    </span>
                    <ChevronDown className="w-4 h-4 text-gray-400 shrink-0" />
                </button>
            )}

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
                        <div className="p-6 pb-7 relative">
                            {/* 우상단 X 닫기 버튼 */}
                            <button
                                onClick={() => setIsOpen(false)}
                                aria-label="닫기"
                                className="absolute top-5 right-5 p-2 text-gray-400 hover:text-gray-600 active:scale-95 rounded-full hover:bg-gray-100 transition-all"
                            >
                                <X className="w-5 h-5" />
                            </button>

                            <div className="flex justify-center mb-6">
                                <div className="w-12 h-1.5 bg-gray-200 rounded-full" />
                            </div>

                            <h3 className="text-xl font-bold text-gray-900 mb-2 px-1 pr-8">
                                자주 가는 도서관을 선택해주세요
                            </h3>
                            <p className="text-gray-500 text-sm mb-6 px-1">
                                선택한 도서관의 청구기호를 보여드립니다.
                            </p>

                            <div className="space-y-2 max-h-[48vh] overflow-y-auto pr-0.5">
                                {availableLibraries.map((lib) => (
                                    <button
                                        key={lib}
                                        onClick={() => handleSelect(lib)}
                                        className={`w-full flex items-center justify-between p-4 rounded-lg text-left transition-all ${selectedLibrary === lib
                                            ? 'bg-brand-primary/10 text-brand-primary font-bold border border-brand-primary/20'
                                            : 'bg-gray-50 text-gray-700 font-medium hover:bg-gray-100 border border-transparent'
                                            }`}
                                    >
                                        <span className="flex items-center gap-3">
                                            <span className={`w-2 h-2 rounded-full ${selectedLibrary === lib ? 'bg-[#F59E0B]' : 'bg-gray-300'}`} />
                                            {lib}
                                        </span>
                                        {selectedLibrary === lib && (
                                            <Check className="w-5 h-5 text-brand-primary" />
                                        )}
                                    </button>
                                ))}
                            </div>

                            {/* 도서관 추가 신청 링크 */}
                            <div className="mt-4 pt-3 border-t border-gray-100 text-center text-xs text-gray-400 break-keep">
                                <span>우리 동네 도서관이 아직 없나요?</span>{' '}
                                <a
                                    href="https://docs.google.com/forms/d/e/1FAIpQLSdz7vpG3dj7RVHUEFWoxjdkEIyALYIry-3J-79bfowT2_82mQ/viewform?usp=publish-editor"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="font-semibold text-gray-600 hover:text-amber-600 underline underline-offset-4 decoration-gray-200 hover:decoration-amber-500 transition-colors ml-1 inline-block"
                                >
                                    도서관 신청하기 ↗
                                </a>
                            </div>
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </>
    )
}
