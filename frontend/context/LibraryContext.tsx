'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

const AVAILABLE_LIBRARIES = ['판교도서관', '송파어린이도서관'] as const
export type LibraryName = typeof AVAILABLE_LIBRARIES[number]

interface LibraryContextType {
    selectedLibrary: LibraryName
    setSelectedLibrary: (library: LibraryName) => void
    availableLibraries: readonly string[]
}

const LibraryContext = createContext<LibraryContextType | undefined>(undefined)

export function LibraryProvider({ children }: { children: ReactNode }) {
    // 기본값은 판교도서관
    const [selectedLibrary, setSelectedLibraryState] = useState<LibraryName>('판교도서관')
    const [isLoaded, setIsLoaded] = useState(false)

    useEffect(() => {
        // 클라이언트 사이드에서만 실행
        const stored = localStorage.getItem('preferred_library')
        if (stored && AVAILABLE_LIBRARIES.includes(stored as any)) {
            setSelectedLibraryState(stored as LibraryName)
        }
        setIsLoaded(true)
    }, [])

    const setSelectedLibrary = (library: LibraryName) => {
        setSelectedLibraryState(library)
        localStorage.setItem('preferred_library', library)
    }

    // Hydration mismatch 방지를 위해 로드되기 전에는 렌더링 하지 않거나 기본값 사용
    // 여기서는 간단히 그냥 리턴 (children은 서버 사이드 렌더링된 내용과 일치해야 하므로 주의)
    // 하지만 Context Provider는 클라이언트 컴포넌트 최상위에 위치하므로 괜찮음.

    return (
        <LibraryContext.Provider value={{ selectedLibrary, setSelectedLibrary, availableLibraries: AVAILABLE_LIBRARIES }}>
            {children}
        </LibraryContext.Provider>
    )
}

export function useLibrary() {
    const context = useContext(LibraryContext)
    if (context === undefined) {
        throw new Error('useLibrary must be used within a LibraryProvider')
    }
    return context
}
