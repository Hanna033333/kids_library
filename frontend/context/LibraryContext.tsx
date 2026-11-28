'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export const VERIFIED_LIBRARIES = [
    '광주광역시립무등도서관',
    '부산광역시 강서기적의도서관',
    '서울특별시교육청서울시립어린이도서관',
    '손기정 어린이도서관',
    '송파어린이도서관',
    '수원시립호매실도서관',
    '수지도서관',
    '아이꿈 작은도서관',
    '울산도서관',
    '판교도서관',
    '평택시립장당도서관',
    '하남시 위례도서관',
    '한밭도서관'
] as const

export type LibraryName = string

export function getStoredPreferredLibrary(): LibraryName | null {
    if (typeof window === 'undefined') return null
    const stored = localStorage.getItem('preferred_library')
    if (stored && stored.trim()) {
        return stored.trim()
    }
    return null
}

export function getStoredPreferredLibraryCode(): string | null {
    if (typeof window === 'undefined') return null
    const stored = localStorage.getItem('preferred_library_code')
    if (stored && stored.trim()) {
        return stored.trim()
    }
    return null
}

interface LibraryContextType {
    selectedLibrary: LibraryName | null
    selectedLibraryCode: string | null
    setSelectedLibrary: (library: LibraryName, code?: string | null) => void
    availableLibraries: readonly string[]
}

export const LibraryContext = createContext<LibraryContextType | undefined>(undefined)

export function LibraryProvider({ children }: { children: ReactNode }) {
    const [selectedLibrary, setSelectedLibraryState] = useState<LibraryName | null>(null)
    const [selectedLibraryCode, setSelectedLibraryCodeState] = useState<string | null>(null)

    useEffect(() => {
        const stored = getStoredPreferredLibrary()
        const storedCode = getStoredPreferredLibraryCode()
        if (stored) {
            setSelectedLibraryState(stored)
        }
        if (storedCode) {
            setSelectedLibraryCodeState(storedCode)
        }

        const handleSignOut = () => {
            setSelectedLibraryState(null)
            setSelectedLibraryCodeState(null)
        }
        window.addEventListener('checkjari:signout', handleSignOut)
        return () => window.removeEventListener('checkjari:signout', handleSignOut)
    }, [])

    const setSelectedLibrary = (library: LibraryName, code?: string | null) => {
        setSelectedLibraryState(library)
        localStorage.setItem('preferred_library', library)
        if (code) {
            setSelectedLibraryCodeState(code)
            localStorage.setItem('preferred_library_code', code)
        } else {
            setSelectedLibraryCodeState(null)
            localStorage.removeItem('preferred_library_code')
        }
    }

    return (
        <LibraryContext.Provider
            value={{
                selectedLibrary,
                selectedLibraryCode,
                setSelectedLibrary,
                availableLibraries: VERIFIED_LIBRARIES,
            }}
        >
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
