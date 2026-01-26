import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getBookById } from '@/lib/api'
import BookDetailClient from './BookDetailClient'

interface Props {
    params: Promise<{ id: string }>
}

// 동적 메타데이터 생성
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    try {
        const { id } = await params
        const book = await getBookById(Number(id))

        if (!book) {
            return {
                title: '책을 찾을 수 없습니다 – 책자리'
            }
        }

        const title = `${book.title} - 책자리`
        // author 필드가 null일 경우 빈 문자열로 처리
        const description = `${book.title} (${book.author || '저자 미상'}). 판교도서관 청구기호 [${book.pangyo_callno}] 및 대출 가능 여부를 실시간으로 확인하세요.`
        const keywords = `${book.title}, ${book.author}, 판교도서관, 청구기호, 어린이 도서, ${book.category || '추천도서'}`

        return {
            title,
            description,
            keywords,
            openGraph: {
                title: `${book.title} - 책자리`,
                description: `판교도서관 청구기호: ${book.pangyo_callno} | 지금 바로 위치와 대출 상태를 확인해보세요.`,
                images: book.image_url ? [book.image_url] : [],
                type: 'article',
            },
            twitter: {
                card: 'summary_large_image',
                title: `${book.title} - 책자리`,
                description,
                images: book.image_url ? [book.image_url] : [],
            },
        }
    } catch (error) {
        console.error('Metadata generation failed:', error);
        return {
            title: '책자리 – 도서관에서 책 찾기',
            description: '도서관 청구기호와 위치 정보를 확인하세요.',
        }
    }
}

// 서버 컴포넌트
export default async function BookDetailPage({ params }: Props) {
    const { id } = await params

    try {
        const book = await getBookById(Number(id))

        if (!book) {
            notFound()
        }

        return <BookDetailClient book={book} />
    } catch (error) {
        console.error('Book fetch failed:', error);
        // 에러 발생 시 404로 처리하거나 별도 에러 페이지로 유도
        notFound();
    }
}
