import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getBookById } from '@/lib/api'
import BookDetailClient from './BookDetailClient'
import { getHighResImageUrl } from '@/lib/utils/image'

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

        const isCaldecott = book.curation_tag?.split(',').includes('caldecott') || book.curation_tag === 'caldecott'
        const title = isCaldecott 
            ? `${book.title} - 칼데콧 메달 수상작 | 책자리 도서 큐레이션`
            : `${book.title} - ${book.category || '어린이 추천 도서'} | 책자리 도서 큐레이션`
        
        const description = isCaldecott
            ? `[칼데콧 메달 수상작] 세계가 인정한 그림책, ${book.title}. 우리 아이의 마음과 정서에 꼭 맞는 엄선 그림책을 만나보세요. ${book.author ? `글/그림: ${book.author}.` : ''}`
            : `${book.title}${book.age ? ` (${book.age} 추천)` : ''}. 우리 아이를 위한 맞춤 추천 도서. 책자리에서 전국 도서관 소장 여부와 실시간 대출 상태를 3초 만에 확인하세요. ${book.author ? `저자: ${book.author}.` : ''}`
        
        const caldecottKeywords = isCaldecott ? '칼데콧 수상작, Caldecott Medal, 그림책 노벨상, ' : ''
        const keywords = `${caldecottKeywords}${book.title}, ${book.author}, 어린이 도서 추천, ${book.category || '그림책'}, ${book.age || ''} 추천도서, 책자리, 도서관 대출 확인, 어린이 도서관`

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
                images: book.image_url ? [getHighResImageUrl(book.image_url)] : [],
                type: 'article',
            },
            twitter: {
                card: 'summary_large_image',
                title,
                description,
                images: book.image_url ? [getHighResImageUrl(book.image_url)] : [],
            },
        }
    } catch (error) {
        console.error('Metadata generation failed:', error);
        return {
            title: '책자리 - 우리 아이를 위한 정서 맞춤 도서 큐레이션',
            description: '우리 아이의 연령과 정서 발달 단계에 꼭 맞는 도서를 발견하고 도서관 대출 현황을 확인하세요.',
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

        const isCaldecott = book.curation_tag?.split(',').includes('caldecott') || book.curation_tag === 'caldecott'

        // Schema.org 구조화 데이터 (JSON-LD)
        // ISBN이 있을 경우 교보문고 BuyAction 추가 -> Google Book Actions 리치 결과 활성화
        const generateKyoboUrl = (isbn: string) => {
            const targetUrl = `https://search.kyobobook.co.kr/search?keyword=${isbn}&gbCode=TOT&target=total`
            const encodedUrl = encodeURIComponent(targetUrl)
            return `https://linkmoa.kr/click.php?m=kbbook&a=A100702199&l=9999&l_cd1=3&l_cd2=0&tu=${encodedUrl}`
        }

        const jsonLd: Record<string, unknown> = {
            '@context': 'https://schema.org',
            '@type': 'Book',
            'url': `https://checkjari.com/book/${book.id}`,
            'name': book.title,
            'isbn': book.isbn || '',
            'author': {
                '@type': 'Person',
                'name': (book.author || '저자 미상').replace(/│/g, ', ')
            },
            'image': getHighResImageUrl(book.image_url) || '',
            'description': isCaldecott 
                ? `[칼데콧 메달 수상작] 세계가 인정한 그림책, ${book.title}. 우리 아이를 위한 최고의 감성 그림책을 책자리에서 확인하세요.`
                : `${book.title}${book.age ? ` (${book.age} 추천)` : ''}. 책자리 큐레이션 도서. 전국 도서관 대출 정보와 교보문고 바로 구매 링크를 연결해 드립니다.`,
            'publisher': {
                '@type': 'Organization',
                'name': book.publisher || '출판사 정보 없음'
            },
            'genre': book.category || '어린이 도서'
        }

        // 칼데콧 수상작인 경우 award 정보 추가
        if (isCaldecott) {
            jsonLd['award'] = 'Caldecott Medal'
        }

        // ISBN이 있을 경우에만 BuyAction 추가 (Book Actions 리치 결과 요건)
        if (book.isbn) {
            jsonLd['potentialAction'] = {
                '@type': 'BuyAction',
                'target': generateKyoboUrl(book.isbn)
            }
        }

        return (
            <>
                <script
                    type="application/ld+json"
                    dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
                />
                <BookDetailClient book={book} />
            </>
        )
    } catch (error) {
        console.error('Book fetch failed:', error);
        // 에러 발생 시 404로 처리하거나 별도 에러 페이지로 유도
        notFound();
    }
}

