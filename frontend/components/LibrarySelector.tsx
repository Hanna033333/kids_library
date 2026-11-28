'use client'

import { useState, useEffect, useCallback } from 'react'
import { useLibrary, LibraryName } from '@/context/LibraryContext'
import { fetchLibraries } from '@/lib/api'
import type { NationalLibrary } from '@/lib/types'
import { ChevronDown, MapPin, Check, X, Navigation } from 'lucide-react'
import { createPortal } from 'react-dom'
import { sendGAEvent } from '@/lib/analytics'

export default function LibrarySelector({
    whiteMode = false,
    autoOpen = false,
    customTrigger,
    displayLibrary,
    onTriggerClick,
    onClose,
}: {
    whiteMode?: boolean
    autoOpen?: boolean
    customTrigger?: (open: () => void) => React.ReactNode
    displayLibrary?: LibraryName | null
    onTriggerClick?: () => void
    onClose?: () => void
}) {
    const { selectedLibrary, setSelectedLibrary } = useLibrary()
    const activeLibrary = displayLibrary !== undefined ? displayLibrary : selectedLibrary
    const [isOpen, setIsOpen] = useState(autoOpen)
    const [isAnimating, setIsAnimating] = useState(false)

    // 전국 도서관 검색 상태
    const [query, setQuery] = useState('')
    const [debouncedQuery, setDebouncedQuery] = useState('')
    const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null)
    const [isLocating, setIsLocating] = useState(false)
    const [locationError, setLocationError] = useState<string | null>(null)
    const [libraries, setLibraries] = useState<NationalLibrary[]>([])
    const [totalCount, setTotalCount] = useState<number>(0)
    const [isLoading, setIsLoading] = useState(false)

    useEffect(() => {
        if (autoOpen) {
            setIsOpen(true)
        }
    }, [autoOpen])

    // 바텀 시트 열기/닫기 애니메이션 처리
    useEffect(() => {
        if (isOpen) {
            setIsAnimating(true)
            document.body.style.overflow = 'hidden'
            return () => {
                document.body.style.overflow = ''
            }
        } else {
            const timer = setTimeout(() => setIsAnimating(false), 300)
            document.body.style.overflow = ''
            return () => clearTimeout(timer)
        }
    }, [isOpen])

    // 검색어 디바운스 (250ms)
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedQuery(query.trim())
        }, 250)
        return () => clearTimeout(timer)
    }, [query])

    // 전국 도서관 API 조회
    useEffect(() => {
        if (!isOpen) return

        let cancelled = false
        const load = async () => {
            setIsLoading(true)
            try {
                const res = await fetchLibraries({
                    q: debouncedQuery || undefined,
                    lat: coords?.lat,
                    lng: coords?.lng,
                    limit: coords ? 20 : 40,
                })
                if (!cancelled) {
                    setLibraries(res.libraries || [])
                    setTotalCount(res.total || 0)
                }
            } catch (err) {
                console.error('전국 도서관 검색 실패:', err)
                if (!cancelled) {
                    setLibraries([])
                    setTotalCount(0)
                }
            } finally {
                if (!cancelled) {
                    setIsLoading(false)
                }
            }
        }

        load()
        return () => {
            cancelled = true
        }
    }, [isOpen, debouncedQuery, coords])

    const handleClose = () => {
        setIsOpen(false)
        onClose?.()
    }

    const handleSelect = (lib: NationalLibrary) => {
        setSelectedLibrary(lib.name, lib.code)
        sendGAEvent('select_library', {
            library: lib.name,
            lib_code: lib.code,
            is_national: !lib.has_callno_db,
        })
        handleClose()
    }

    const handleLocateNearby = useCallback(() => {
        setLocationError(null)
        if (typeof window === 'undefined' || !navigator.geolocation) {
            setLocationError('이 기기에서는 위치 기능을 지원하지 않습니다. 도서관 이름을 검색해주세요.')
            return
        }
        setIsLocating(true)
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                setCoords({
                    lat: pos.coords.latitude,
                    lng: pos.coords.longitude,
                })
                setQuery('')
                setIsLocating(false)
                sendGAEvent('click_nearby_libraries', {})
            },
            (err) => {
                if (err.code === err.PERMISSION_DENIED) {
                    setLocationError('위치 권한을 허용하면 가까운 도서관을 바로 찾을 수 있어요.')
                } else {
                    setLocationError('현재 위치를 확인하지 못했어요. 잠시 후 다시 시도하거나 도서관 이름을 검색해주세요.')
                }
                setIsLocating(false)
            },
            { enableHighAccuracy: false, timeout: 8000 }
        )
    }, [])

    const displayLibraryName = activeLibrary
        ? (activeLibrary.length > 15 ? `${activeLibrary.slice(0, 15)}...` : activeLibrary)
        : '도서관을 선택해주세요'

    return (
        <>
            {/* Trigger Button */}
            {customTrigger ? (
                customTrigger(() => {
                    if (onTriggerClick) {
                        onTriggerClick()
                    } else {
                        setIsOpen(true)
                    }
                })
            ) : (
                <button
                    type="button"
                    onClick={() => {
                        if (onTriggerClick) {
                            onTriggerClick()
                        } else {
                            setIsOpen(true)
                        }
                    }}
                    className={`flex items-center gap-1.5 text-sm sm:text-base font-bold py-1 px-0.5 transition-colors shrink-0 max-w-full outline-none focus:outline-none ${whiteMode
                        ? 'text-white active:text-white/80'
                        : activeLibrary
                            ? 'text-gray-900 active:text-gray-700 font-black'
                            : 'text-gray-400 active:text-gray-600 font-medium'
                        }`}
                >
                    <MapPin className={`w-4 h-4 shrink-0 ${whiteMode ? 'text-white' : activeLibrary ? 'text-amber-500' : 'text-gray-400'}`} />
                    <span className="truncate underline decoration-gray-300 underline-offset-4">
                        {displayLibraryName}
                    </span>
                    <ChevronDown className="w-4 h-4 text-gray-400 shrink-0" />
                </button>
            )}

            {/* Bottom Sheet Portal */}
            {(isOpen || isAnimating) && createPortal(
                <div className="fixed inset-0 z-[100] flex justify-center items-end sm:items-center pointer-events-none">
                    {/* Overlay */}
                    <div
                        className={`absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity duration-300 pointer-events-auto ${isOpen ? 'opacity-100' : 'opacity-0'}`}
                        onClick={handleClose}
                    />

                    {/* Sheet */}
                    <div
                        className={`w-full max-w-md bg-white rounded-t-[28px] sm:rounded-[28px] shadow-2xl overflow-hidden pointer-events-auto transition-transform duration-300 transform ${isOpen ? 'translate-y-0 scale-100' : 'translate-y-full sm:translate-y-8 sm:scale-95'
                            } safe-area-bottom`}
                    >
                        <div className="p-6 pb-7 relative">
                            {/* 우상단 X 닫기 버튼 */}
                            <button
                                type="button"
                                onClick={handleClose}
                                aria-label="닫기"
                                className="absolute top-5 right-5 p-2 text-gray-400 active:scale-95 rounded-full active:bg-gray-100 transition-all outline-none focus:outline-none"
                            >
                                <X className="w-5 h-5" />
                            </button>

                            <div className="flex justify-center mb-5">
                                <div className="w-12 h-1.5 bg-gray-200 rounded-full" />
                            </div>

                            <h3 className="text-xl font-bold text-gray-900 mb-1.5 px-1 pr-8">
                                우리 동네 도서관 선택
                            </h3>
                            <p className="text-gray-500 text-sm mb-4 px-1">
                                전국 1,600+ 공공도서관의 실시간 대출 여부를 확인해요.
                            </p>

                            {/* 검색 입력창 (아이콘 미삽입 규약 준수, 1.5px 보더 + focus Primary) */}
                            <div className="flex gap-2 mb-3">
                                <input
                                    type="text"
                                    value={query}
                                    onChange={(e) => {
                                        setQuery(e.target.value)
                                        if (coords) setCoords(null)
                                    }}
                                    placeholder="도서관 이름 또는 동네명 (예: 강남, 분당, 해운대)"
                                    className="flex-1 min-h-[48px] px-4 py-2.5 text-sm text-gray-900 bg-white border-[1.5px] border-gray-200 rounded-xl focus:border-brand-primary outline-none transition-colors placeholder:text-gray-400"
                                />
                                {query && (
                                    <button
                                        type="button"
                                        onClick={() => setQuery('')}
                                        className="min-h-[48px] px-3 text-xs font-semibold text-gray-500 bg-gray-100 rounded-xl active:bg-gray-200 shrink-0 outline-none focus:outline-none"
                                    >
                                        지우기
                                    </button>
                                )}
                            </div>

                            {/* 내 주변 도서관 찾기 버튼 */}
                            <div className="mb-3">
                                <button
                                    type="button"
                                    onClick={handleLocateNearby}
                                    disabled={isLocating}
                                    className={`w-full min-h-[48px] px-4 py-2.5 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-all outline-none focus:outline-none ${coords
                                        ? 'bg-brand-primary text-white active:bg-brand-primary-dark'
                                        : 'bg-amber-50 text-amber-800 border border-amber-200 active:bg-amber-100'
                                        } disabled:opacity-50`}
                                >
                                    <Navigation className="w-4 h-4 shrink-0" />
                                    <span>{coords ? '내 주변 가까운 도서관 보기 중' : '내 주변 도서관 찾기'}</span>
                                </button>
                                {locationError && (
                                    <p className="mt-1.5 px-1 text-xs text-red-500">{locationError}</p>
                                )}
                            </div>

                            {/* 검색 결과 개수 안내 */}
                            <div className="flex items-center justify-between px-1 mb-2 text-xs text-gray-400">
                                <span>
                                    {coords
                                        ? '현재 위치에서 가까운 순'
                                        : debouncedQuery
                                            ? `검색 결과 ${totalCount.toLocaleString()}곳`
                                            : `전국 공공도서관 ${totalCount.toLocaleString()}곳`}
                                </span>
                                {coords && (
                                    <button
                                        type="button"
                                        onClick={() => setCoords(null)}
                                        className="text-gray-500 underline underline-offset-2 font-medium outline-none focus:outline-none"
                                    >
                                        전체 목록으로
                                    </button>
                                )}
                            </div>

                            {/* 도서관 리스트 */}
                            <div className="space-y-2 max-h-[45vh] overflow-y-auto pr-0.5">
                                {isLoading ? (
                                    <div className="space-y-2 py-2">
                                        {[1, 2, 3, 4].map((i) => (
                                            <div key={i} className="h-[60px] rounded-xl bg-gray-100 animate-pulse" />
                                        ))}
                                    </div>
                                ) : libraries.length === 0 ? (
                                    <div className="py-10 text-center text-sm text-gray-400">
                                        검색 조건에 맞는 도서관이 없습니다.<br />
                                        다른 지역이나 동네 이름으로 검색해보세요.
                                    </div>
                                ) : (
                                    libraries.map((lib) => {
                                        const isSelected = selectedLibrary === lib.name
                                        return (
                                            <button
                                                key={lib.code}
                                                type="button"
                                                onClick={() => handleSelect(lib)}
                                                className={`w-full min-h-[56px] flex items-center justify-between gap-3 px-4 py-3 rounded-xl text-left transition-all outline-none focus:outline-none ${isSelected
                                                    ? 'bg-brand-primary/10 text-brand-primary font-bold border border-brand-primary/30'
                                                    : 'bg-gray-50 text-gray-800 font-medium active:bg-gray-100 border border-transparent'
                                                    }`}
                                            >
                                                <div className="min-w-0 flex-1">
                                                    <div className="flex items-center gap-2">
                                                        <span className={`text-sm truncate ${isSelected ? 'font-bold text-brand-primary' : 'font-semibold text-gray-900'}`}>
                                                            {lib.name}
                                                        </span>
                                                        {lib.distance_km !== undefined && (
                                                            <span className="shrink-0 text-[11px] font-bold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded-md">
                                                                {lib.distance_km < 1
                                                                    ? `${Math.round(lib.distance_km * 1000)}m`
                                                                    : `${lib.distance_km.toFixed(1)}km`}
                                                            </span>
                                                        )}
                                                    </div>
                                                    {lib.address && (
                                                        <p className="text-xs text-gray-500 truncate mt-0.5 font-normal">
                                                            {lib.address}
                                                        </p>
                                                    )}
                                                </div>
                                                {isSelected && (
                                                    <Check className="w-5 h-5 text-brand-primary shrink-0" />
                                                )}
                                            </button>
                                        )
                                    })
                                )}
                            </div>
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </>
    )
}
