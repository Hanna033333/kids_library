'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'
import { supabase } from '@/lib/supabase'
import { getSavedBookIds } from '@/lib/supabase-api'
import { getBooksByIds, fetchLoanStatuses } from '@/lib/api'
import { Book } from '@/lib/types'
import BookItem from '@/components/BookItem'
import { Loader2, BookOpen } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ProfileDropdown from '@/components/ProfileDropdown'
import PageHeader from '@/components/PageHeader'
import { Spinner } from '@/components/ui/Spinner'
import { PageLoader } from '@/components/ui/PageLoader'

export default function MyLibraryPage() {
    const { user, isLoading: authLoading } = useAuth()
    const [books, setBooks] = useState<Book[]>([])
    const [isLoading, setIsLoading] = useState(true)
    // const supabase = createClient() <-- 제거됨
    const router = useRouter()

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/')
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
            <PageLoader />
        )
    }

    return (
        <main className="min-h-screen bg-[#F7F7F7]">
            {/* Header */}
            <PageHeader title="내 책장" backHref="/" rightSlot={<ProfileDropdown />} />

            <div className="max-w-7xl mx-auto px-6 py-10">
                <div className="mb-8">
                    <p className="text-gray-500 font-medium">총 {books.length}권</p>
                </div>

                {books.length === 0 ? (
                    <div className="py-20 flex flex-col items-center justify-center text-center">
                        <p className="text-gray-600 font-bold text-lg mb-1">아직 담아둔 책이 없어요</p>
                        <p className="text-gray-400 text-sm mb-6">책을 담고 청구기호를 한눈에 확인해 보세요</p>
                        <Link
                            href="/"
                            className="px-6 py-3 bg-[#F59E0B] text-white rounded-lg font-semibold transition-all"
                        >
                            책 보러 가기
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        {books.map((book) => (
                            <BookItem key={book.id} book={book} loanStatus={book.loan_status ?? undefined} />
                        ))}
                    </div>
                )}
            </div>
        </main>
    )
}
