import { cache } from 'react'
import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import BookDetailClient from './BookDetailClient'
import { getHighResImageUrl } from '@/lib/utils/image'
import { createClient } from '@/lib/supabase'
import { getBooksByTag, getBooksByTopicTag, getTextbookBooks, getPopularBooksByAge, getBooksByAuthor } from '@/lib/home-api'
import { getAgeGroupKey } from '@/lib/utils/age'
import { getPrimaryCurationTag, getTopicCurationTag, extractGradeTag, isSpecialTag } from '@/lib/utils/curation-filter'
import { sanitizeDescriptionHtml } from '@/lib/utils/sanitize-html'

interface Props {
    params: Promise<{ id: string }>
}

// 24시간마다 백그라운드 재검증 (ISR)
export const revalidate = 86400
export const dynamicParams = true

// 빌드 타임에 상위 100개의 핵심 도서 상세 페이지를 정적 프리렌더링하여 초고속 응답 보장
// (API 서버 오프라인으로 인한 빌드 에러 방지를 위해 Supabase 직접 조회 사용)
export async function generateStaticParams() {
    try {
        const supabase = createClient()
        const { data: books } = await supabase
            .from('childbook_items')
            .select('id')
            .or('is_hidden.is.null,is_hidden.eq.false')
            .order('id', { ascending: true })
            .limit(100)

        if (!books) return []
        return books.map((book) => ({
            id: String(book.id),
        }))
    } catch (e) {
        console.error('Failed to generate static params:', e)
        return []
    }
}

// React cache()로 래핑하여 generateMetadata와 페이지 컴포넌트 간 중복 DB 쿼리 제거
// (동일 렌더링 요청 내에서 같은 인자로 호출 시 결과를 공유)
const getBookDetailServer = cache(async (id: number) => {
    const supabase = createClient()
    
    // 1. 책 기본 정보 (이후 쿼리의 선행 조건)
    const { data: book, error } = await supabase
        .from('childbook_items')
        .select('*')
        .eq('id', id)
        .maybeSingle()

    if (error || !book) return null

    // 2+3. 찜 횟수 & 도서관 소장 정보를 Promise.all로 병렬 조회 (직렬 3회 → 병렬 2회로 단축)
    const [{ count }, { data: libInfo }] = await Promise.all([
        supabase
            .from('wishlists')
            .select('id', { count: 'exact', head: true })
            .eq('book_id', id),
        supabase
            .from('book_library_info')
            .select('library_name, callno')
            .eq('book_id', id)
    ])

    return {
        ...book,
        save_count: count || 0,
        library_info: libInfo || []
    }
})

// 동적 메타데이터 생성
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    try {
        const { id } = await params
        const book = await getBookDetailServer(Number(id))

        if (!book) {
            return {
                title: '책을 찾을 수 없습니다 – 책자리'
            }
        }

        const isCaldecott = book.curation_tag?.split(',').includes('caldecott') || book.curation_tag === 'caldecott'
        const isTextbook = book.curation_tag?.includes('교과서수록') || book.curation_tag?.includes('textbook')

        let title = `${book.title} | 내 주변 도서관 책 검색 & 실시간 대출 상태`
        let description = `[도서관 헛걸음 방지] "${book.title}"${book.age ? ` (${book.age} 추천)` : ''} 도서의 내 주변 도서관 책 검색, 실시간 대출 가능 상태와 청구기호 확인까지 책자리에서 3초 만에 조회하세요.`

        if (isCaldecott) {
            title = `${book.title} | 칼데콧 메달 수상작 & 주변 도서관 책 검색`
            description = `[도서관 헛걸음 방지] 세계가 인정한 칼데콧 수상작, "${book.title}". 우리 아이 마음 발달에 꼭 맞는 그림책을 발견하고, 내 주변 도서관 실시간 대출 가능 상태와 청구기호를 3초 만에 확인하세요.`
        } else if (isTextbook) {
            title = `[초등 교과서 수록] ${book.title} | 내 주변 도서관 책 검색 & 실시간 대출`
            description = `[초등 교과서 수록도서] 초등학교 국어 교과서에 실린 "${book.title}"${book.age ? ` (${book.age} 추천)` : ''}. 내 주변 도서관 실시간 대출 가능 상태와 청구기호를 책자리에서 3초 만에 확인하세요.`
        }
        
        const caldecottKeywords = isCaldecott ? '칼데콧 수상작, Caldecott Medal, 그림책 노벨상, ' : ''
        const textbookKeywords = isTextbook ? '초등 교과서 수록도서, 교과서 수록 도서, 초등 국어 교과서, 초등 필독서, ' : ''
        const keywords = `주변 도서관 책 검색, ${caldecottKeywords}${textbookKeywords}${book.title}, ${book.author}, 어린이 도서 추천, ${book.category || '그림책'}, ${book.age || ''} 추천도서, 책자리, 도서관 대출 확인, 어린이 도서관`

        const fullTitle = `${title} | 책자리`

        return {
            title,
            description,
            keywords,
            alternates: {
                canonical: `/book/${id}`
            },
            openGraph: {
                title: fullTitle,
                description,
                images: book.image_url ? [getHighResImageUrl(book.image_url)] : [],
                type: 'article',
            },
            twitter: {
                card: 'summary_large_image',
                title: fullTitle,
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
        const book = await getBookDetailServer(Number(id))

        if (!book) {
            notFound()
        }

        const ageGroupKey = getAgeGroupKey(book.age)

        // 1. 대표 큐레이션 태그: 교과서수록, 칼데콧 등 특수 태그 우선 선정
        const primaryTag = getPrimaryCurationTag(book.curation_tag)
        // 2. 순수 AI 주제 태그: 특수 태그 및 학년 태그 제외
        const topicTag = getTopicCurationTag(book.curation_tag)
        const gradeTag = extractGradeTag(book.curation_tag)
        const hasDistinctTopicTag = Boolean(topicTag && topicTag !== primaryTag)

        // 1번 대표 큐레이션 도서 쿼리 결정 (교과서는 학년 연동, 일반 주제는 연령 타겟팅)
        const fetchPrimaryBooks = () => {
            if (!primaryTag) return Promise.resolve([])
            if (primaryTag === '교과서수록') {
                return getTextbookBooks(gradeTag || undefined, 8)
            }
            if (isSpecialTag(primaryTag)) {
                return getBooksByTag(primaryTag, 8)
            }
            return getBooksByTopicTag(primaryTag, 8, { age: book.age, gradeTag })
        }

        // 추천 도서를 Promise.all로 병렬 조회 (직렬 호출 방지)
        // getPopularBooksByAge를 14권으로 호출하여 폴백+연령 추천에 공용 사용
        const [rawCurationBooks, rawTopicBooks, rawAgeBooks, authorRecommended] = await Promise.all([
            fetchPrimaryBooks(),
            hasDistinctTopicTag ? getBooksByTopicTag(topicTag, 8, { age: book.age, gradeTag }) : Promise.resolve([]),
            getPopularBooksByAge(ageGroupKey, 14),
            book.author ? getBooksByAuthor(book.author, book.id, 7) : Promise.resolve([])
        ])

        // 1. 대표/교과서 큐레이션 추천 도서 구성 (7권)
        let curationRecommended = rawCurationBooks
            .filter((b: any) => b.id !== book.id)
            .slice(0, 7)

        // 폴백: 동일 큐레이션 추천 도서가 7권 미만인 경우 연령별 인기 도서(rawAgeBooks)로 채움
        if (curationRecommended.length < 7) {
            const needCount = 7 - curationRecommended.length
            const filteredFallback = rawAgeBooks.filter(
                (b: any) => b.id !== book.id && !curationRecommended.some((cr: any) => cr.id === b.id)
            )
            curationRecommended = [...curationRecommended, ...filteredFallback.slice(0, needCount)]
        }

        // 2. 연령별 인기 추천 도서 (7권) — rawAgeBooks 재활용 (추가 쿼리 없음)
        const ageRecommended = rawAgeBooks
            .filter((b: any) => b.id !== book.id)
            .slice(0, 7)

        // 3. AI 순수 주제 태그 추천 도서 구성 (7권 - 교과서/특수 도서 대상)
        let topicRecommended: any[] = []
        if (hasDistinctTopicTag) {
            topicRecommended = rawTopicBooks
                .filter((b: any) => b.id !== book.id)
                .slice(0, 7)

            // 폴백: 주제 도서가 부족한 경우 연령별 인기 도서로 채우되, 2번 연령 추천 섹션과 겹치지 않는 도서 우선 바인딩
            if (topicRecommended.length < 7) {
                const needCount = 7 - topicRecommended.length
                const filteredFallback = rawAgeBooks.filter(
                    (b: any) => b.id !== book.id && 
                        !topicRecommended.some((tr: any) => tr.id === b.id) &&
                        !ageRecommended.some((ar: any) => ar.id === b.id)
                )
                topicRecommended = [...topicRecommended, ...filteredFallback.slice(0, needCount)]
            }
        }

        const isCaldecott = book.curation_tag?.split(',').includes('caldecott') || book.curation_tag === 'caldecott'
        const isTextbook = book.curation_tag?.includes('교과서수록') || book.curation_tag?.includes('textbook')

        // Schema.org 구조화 데이터 (JSON-LD)
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
                : isTextbook
                ? `[초등 국어 교과서 수록도서] 초등학교 교과서에 실린 ${book.title}${book.age ? ` (${book.age} 추천)` : ''}. 전국 도서관 대출 정보와 청구기호를 확인하세요.`
                : `${book.title}${book.age ? ` (${book.age} 추천)` : ''}. 책자리 큐레이션 도서. 전국 도서관 대출 정보와 교보문고 바로 구매 링크를 연결해 드립니다.`,
            'publisher': {
                '@type': 'Organization',
                'name': book.publisher || '출판사 정보 없음'
            },
            'genre': isTextbook ? '초등 교과서 수록도서' : (book.category || '어린이 도서')
        }

        if (isCaldecott) {
            jsonLd['award'] = 'Caldecott Medal'
        }

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
                
                {/* 1번 전략: 검색 로봇 봇을 위한 오리지널 정적 시맨틱 텍스트 구조 */}
                {/* 검색 봇(네이버, 구글)은 Javascript가 배제된 원본 HTML 파싱 시점에 큐레이션 해설과 상세 소개를 완벽하게 인덱싱합니다. */}
                <article className="hidden" aria-hidden="true" style={{ display: 'none' }}>
                    <h1>{book.title}</h1>
                    <p>저자: {book.author}</p>
                    <p>출판사: {book.publisher}</p>
                    <p>연령: {book.age}</p>
                    <p>분류: {book.category}</p>
                    {book.curation_note && (
                        <section>
                            <h2>책자리 AI 전문 사서의 정서/상황별 맞춤 큐레이션 코멘트</h2>
                            <p>{book.curation_note}</p>
                        </section>
                    )}
                    {book.description && (
                        <section>
                            <h2>도서 상세 소개</h2>
                            <div dangerouslySetInnerHTML={{ __html: sanitizeDescriptionHtml(book.description) }} />
                        </section>
                    )}
                </article>

                <BookDetailClient 
                    book={book} 
                    curationRecommended={curationRecommended} 
                    ageRecommended={ageRecommended} 
                    topicRecommended={topicRecommended}
                    authorRecommended={authorRecommended}
                />
            </>
        )
    } catch (error) {
        console.error('Book fetch failed:', error);
        notFound();
    }
}

