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

        const title = `${book.title} - 도서관 청구기호/위치 3초 확인 (책자리)`
        // author 필드가 null일 경우 빈 문자열로 처리
        const description = `${book.title}의 청구기호, 도서관 위치, 대출 가능 여부를 로그인 없이 확인하세요. 어린이 추천 도서.`
        const keywords = `${book.title}, ${book.author}, 도서관, 청구기호, 어린이 도서, ${book.category || '추천도서'}, 4~7세 추천 도서, 초등 필독서, 도서관 위치, 청구기호 찾기, 책자리, 판교도서관`

        return {
            title,
            description,
            keywords,
            alternates: {
                canonical: `/book/${id}`
            },
            openGraph: {
                title,
                description,
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
