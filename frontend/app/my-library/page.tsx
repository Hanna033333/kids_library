'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'
import { createClient } from '@/lib/supabase'
import { getSavedBookIds } from '@/lib/supabase-api'
import { getBooksByIds, fetchLoanStatuses } from '@/lib/api'
import { Book } from '@/lib/types'
import BookItem from '@/components/BookItem'
import { Bookmark, ChevronLeft, Loader2, BookOpen } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function MyLibraryPage() {
    const { user, isLoading: authLoading } = useAuth()
    const [books, setBooks] = useState<Book[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const supabase = createClient()
    const router = useRouter()

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/auth')
        }
    }, [user, authLoading, router])

    useEffect(() => {
        const fetchSavedBooks = async () => {
            if (!user) return
            setIsLoading(true)
            try {
                const savedIds = await getSavedBookIds(supabase, user.id)
                if (savedIds.length === 0) {
                    setBooks([])
                    return
                }

                const booksData = await getBooksByIds(savedIds)

                // Fetch loan statuses in background
                setBooks(booksData)

                const loanStatuses = await fetchLoanStatuses(savedIds)
                const updatedBooks = booksData.map(book => ({
                    ...book,
                    loan_status: loanStatuses[book.id] || null
                }))
                setBooks(updatedBooks)
            } catch (err) {
                console.error('Failed to fetch saved books:', err)
            } finally {
                setIsLoading(false)
            }
        }

        if (user) {
            fetchSavedBooks()
        }
    }, [user, supabase])

    if (authLoading || (isLoading && books.length === 0)) {
        return (
            <div className="min-h-screen bg-[#F7F7F7] flex flex-col items-center justify-center">
                <Loader2 className="w-10 h-10 text-blue-600 animate-spin mb-4" />
                <p className="text-gray-500 font-medium">내 서재를 불러오는 중...</p>
            </div>
        )
    }

    return (
        <main className="min-h-screen bg-[#F7F7F7]">
            {/* Header */}
            <header className="w-full bg-white border-b border-gray-100 flex items-center justify-between px-6 py-4 sticky top-0 z-50">
                <div className="w-1/3">
                    <Link
                        href="/"
                        className="flex items-center gap-1 text-gray-500 hover:text-gray-900 transition-colors font-medium text-sm"
                    >
                        <ChevronLeft className="w-5 h-5" />
                        <span>돌아가기</span>
                    </Link>
                </div>
                <div className="w-1/3 flex justify-center">
                    <h1 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                        <Bookmark className="w-5 h-5 text-blue-600 fill-current" />
                        내 서재
                    </h1>
                </div>
                <div className="w-1/3"></div>
            </header>

            <div className="max-w-7xl mx-auto px-6 py-10">
                <div className="mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">내가 찜한 책들</h2>
                    <p className="text-gray-500">총 {books.length}권의 책이 저장되어 있습니다.</p>
                </div>

                {books.length === 0 ? (
                    <div className="bg-white rounded-xl border border-dashed border-gray-200 py-20 flex flex-col items-center justify-center text-center">
                        <div className="bg-blue-50 p-4 rounded-full mb-4">
                            <BookOpen className="w-8 h-8 text-blue-400" />
                        </div>
                        <p className="text-gray-600 font-bold text-lg mb-1">저장된 책이 없습니다.</p>
                        <p className="text-gray-400 text-sm mb-6">마음에 드는 책을 발견하면 하트를 눌러보세요!</p>
                        <Link
                            href="/"
                            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-all shadow-lg shadow-blue-100"
                        >
                            책 구경하러 가기
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        {books.map((book) => (
                            <BookItem key={book.id} book={book} />
                        ))}
                    </div>
                )}
            </div>
        </main>
    )
}
