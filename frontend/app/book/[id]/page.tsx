import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getBookById } from '@/lib/api'
import BookDetailClient from './BookDetailClient'

interface Props {
    params: Promise<{ id: string }>
}

// 동적 메타데이터 생성
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { id } = await params
    const book = await getBookById(Number(id))

    if (!book) {
        return {
            title: '책을 찾을 수 없습니다 – 책자리'
        }
    }

    const title = `${book.title} | 도서관에서 책 위치 찾기 – 책자리`
    const description = `${book.title} - ${book.author || ''}. 판교도서관 청구기호: ${book.pangyo_callno}`

    return {
        title,
        description,
        openGraph: {
            title: `${book.title} | 도서관에서 책 위치 찾기`,
            description: `${book.author || ''} | 청구기호: ${book.pangyo_callno}`,
            images: book.image_url ? [book.image_url] : [],
            type: 'article',
        },
        twitter: {
            card: 'summary_large_image',
            title,
            description,
            images: book.image_url ? [book.image_url] : [],
        },
    }
}

// 서버 컴포넌트
export default async function BookDetailPage({ params }: Props) {
    const { id } = await params
    const book = await getBookById(Number(id))

    if (!book) {
        notFound()
    }

    return <BookDetailClient book={book} />
}
