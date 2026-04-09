'use client'

import BookItem from '@/components/BookItem'
import { Book } from '@/lib/types'

import { PageLoader } from '@/components/ui/PageLoader'

interface CaldecottClientProps {
    books: Book[]
}

export default function CaldecottClient({ books }: CaldecottClientProps) {
    return (
        <>
            {books.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    {books.map((book) => (
                        <BookItem key={book.id} book={book} />
                    ))}
                </div>
            ) : (
                <PageLoader />
            )}
        </>
    )
}
