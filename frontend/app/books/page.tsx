import BooksPageClient from "@/components/BooksPageClient";
import { Metadata } from 'next'
import { VALID_TAXONOMY, VALID_AI_TAGS } from '@/lib/constants/taxonomy'
import { Suspense } from 'react'
import { PageLoader } from '@/components/ui/PageLoader'

interface Props {
    searchParams: { age?: string; curation?: string; category?: string; q?: string }
}

export async function generateMetadata({ searchParams }: Props): Promise<Metadata> {
    const { age: rawAge, curation: rawCuration, q } = searchParams
    const curation = rawCuration ? decodeURIComponent(rawCuration) : undefined
    const age = rawAge ? decodeURIComponent(rawAge) : undefined

    let title = '책자리 - 우리 아이 상황별 맞춤 도서 큐레이션'
    let description = '어떤 책을 읽혀야 할지 고민되는 부모님을 위해! 아이의 연령과 정서적 상황(잠자리, 사회성, 감정 발달 등)에 딱 맞는 전문가 엄선 도서 큐레이션 목록과 전국 도서관 소장 정보 및 바로 구매를 확인해 보세요.'
    let keywords = '어린이 도서 추천, 아동 도서 검색, 도서 큐레이션, 어린이 정서 발달, 상황별 그림책, 도서 대출 확인'

    const matchedTaxonomy = VALID_TAXONOMY.find(item => item.tag === curation);

    if (curation === 'winter-vacation' || curation === '겨울방학') {
        title = '스마트폰만 보는 아이, 방학 때 뭐 읽힐까요?'
        description = '사서가 직접 뽑았다! 실패 없는 겨울방학 추천도서 리스트를 도서관에서 바로 대출하세요. 초등학생 필독서부터 인기 베스트까지 한눈에 확인하세요.'
        keywords = '겨울방학 독서 숙제, 초등 겨울방학 추천도서, 문해력 향상 도서, 독서록 쓰기 좋은 책, 학년별 추천 도서, 사서 추천'
    } else if (curation === 'research-council' || curation === '어린이도서연구회') {
        title = "전문가가 보증하는 '찐' 필독서 모음 | 어린이도서연구회 추천도서"
        description = '엄마표 독서 고민 끝! 어린이 도서 연구회가 엄선한 필독서를 도서관에서 바로 대출하세요. 전문가 추천 베스트 어린이 책 리스트를 지금 확인하세요.'
        keywords = '어린이 도서 연구회, 전문가 추천 도서, 사서 추천, 어린이 필독서, 베스트 어린이 책, 권장도서'
    } else if (curation === 'caldecott') {
        title = "2000-2026 칼데콧 수상작 | 세계 최고의 어린이 그림책 리스트 - 책자리"
        description = '2000년부터 2026년까지 칼데콧 메달을 수상한 세계 최고의 어린이 그림책 목록입니다. 전국 도서관 소장 여부와 실시간 대출 정보를 확인하고 바로 읽혀보세요.'
        keywords = '칼데콧상, Caldecott Medal, 어린이 그림책, 수상작, 추천 도서, 전국 도서관 대출, 그림책 노벨상'
    } else if (matchedTaxonomy) {
        title = `${matchedTaxonomy.subtitle} | ${matchedTaxonomy.title} - 책자리`
        description = `"${matchedTaxonomy.subtitle}" 우리 아이의 마음 and 정서에 꼭 맞는 '${matchedTaxonomy.tag}' 엄선 그림책 리스트! 주변 도서관 소장 상태, 대출 정보 및 교보문고 바로 구매 링크를 만나보세요.`
        keywords = `${matchedTaxonomy.tag}, ${matchedTaxonomy.title}, 그림책 큐레이션, 그림책 추천, 어린이 도서, 책자리, 부모 필독서, 정서 발달`
    } else if (age) {
        // 다양한 연령대 입력(예: 0-3, 0-2세, 3-4세, 4-7, 5-7세 등)을 지원하기 위해 정규화
        const ageClean = age.replace(/\s+/g, '');
        if (ageClean === '0-3' || ageClean === '0-2세' || ageClean.includes('0세') || ageClean.includes('1세') || ageClean.includes('2세') || ageClean.includes('3세')) {
            title = '0~3세 영유아 그림책 추천, 신체 발달과 감각 자극 맞춤 단권 | 책자리'
            description = '전집 고민 그만! 0세, 1세, 2세, 3세 우리 아기 신체 발달과 감각 자극에 딱 맞는 연령별 추천 그림책 리스트를 지금 만나보세요.'
            keywords = '3세 그림책, 3세 책 추천 단권, 0-3세 추천 도서, 영유아 그림책, 아기2살 책종류, 3-4개월 아기 책추천'
        } else if (ageClean === '4-7' || ageClean === '3-4세' || ageClean === '5-7세' || ageClean.includes('4세') || ageClean.includes('5세') || ageClean.includes('6세') || ageClean.includes('7세') || ageClean.includes('유치원')) {
            title = '7세 책 추천 리스트, 전집 대신 상황별 맞춤 단권으로! | 책자리'
            description = '초등 입학 전, 어떤 책을 읽혀야 할지 막막하신가요? 7세 발달 단계와 사서가 엄선한 실패 없는 단권 도서 리스트를 3초 만에 확인하고 도서관 대출 여부까지 즉시 조회하세요.'
            keywords = '7세 책 추천 리스트, 유치원생 필독도서, 유치원생 책 추천, 7세 추천도서 그림책, 7세 동화책 추천순, 도서관 책 소장 검색'
        } else if (ageClean === '8-12' || ageClean === '8-13세' || ageClean.includes('8세') || ageClean.includes('9세') || ageClean.includes('10세') || ageClean.includes('11세') || ageClean.includes('12세') || ageClean.includes('초등')) {
            title = '8~12세 초등 필독서 추천, 아이의 문해력과 자존감을 키우는 책 | 책자리'
            description = '초등학생 자녀의 어휘력과 자존감, 정서 발달을 키워줄 상황별 필독 동화책 목록! 전국 도서관 대출 가능 상태와 교보문고 바로 구매를 확인하세요.'
            keywords = '8세 스테디셀러 동화, 초등학생 필독서, 초등 추천 도서, 학년별 권장도서, 사서 추천'
        } else {
            title = `우리 아이 나이에 딱! ${age} 맞춤 도서 - 책자리`
            description = `우리 아이 ${age} 연령대 발달 단계와 정서적 필요에 딱 맞춘 추천 그림책과 동화책 리스트! 내 주변 도서관 대출 여부와 교보 구매까지 즉시 연결해 드립니다.`
            keywords = `${age} 추천 도서, 어린이 책 추천, 학년별 권장도서, 책자리`
        }
    } else if (q) {
        title = `"${q}" 검색 결과 - 우리 아이 맞춤 도서 추천 | 책자리`
        description = `도서관 가기 전 헛걸음 방지! "${q}" 도서의 전국 도서관 대출 가능 여부, 소장 상태 및 교보문고 바로 구매 링크를 빠르게 확인하세요.`
        keywords = `${q}, 도서 검색, 어린이 도서 큐레이션, 도서 대출 확인, 책자리`
    }

    // Generate canonical URL with query parameters
    const params = new URLSearchParams(searchParams as any).toString()
    const canonicalUrl = params ? `/books?${params}` : '/books'

    return {
        title,
        description,
        keywords,
        alternates: {
            canonical: canonicalUrl
        },
        openGraph: {
            title,
            description,
            type: 'website',
            url: `https://checkjari.com/books?${new URLSearchParams(searchParams as any).toString()}`
        },
        twitter: {
            card: 'summary_large_image',
            title,
            description
        }
    }
}

import { createClient } from '@/lib/supabase-server'

export const dynamic = 'force-dynamic';

export default async function BooksPage({ searchParams }: Props) {
    const { curation: rawCuration } = searchParams
    const curation = rawCuration ? decodeURIComponent(rawCuration) : undefined
    let jsonLd = null;

    // curation 값이 있고, 알려진 큐레이션 태그인 경우 서버 사이드에서 데이터를 가져와 구조화된 데이터 생성
    const isKnownCuration = ['winter-vacation', 'research-council', 'caldecott'].includes(curation || '') || 
                            (curation && VALID_AI_TAGS.includes(curation));
    if (curation && isKnownCuration) {
        const supabase = createClient()
        let query = supabase
            .from('childbook_items')
            .select('id, title, author, isbn, image_url')
            .or('is_hidden.is.null,is_hidden.eq.false')

        const SPECIAL_TAGS = ['winter-vacation', 'research-council', 'caldecott', '겨울방학2026', '어린이도서연구회'];
        if (SPECIAL_TAGS.includes(curation)) {
            query = query.ilike('curation_tag', `%${curation}%`);
        } else {
            const orFilter = `curation_tag.eq."${curation}",curation_tag.like."${curation},%",curation_tag.eq."#${curation}",curation_tag.like."#${curation},%"`;
            query = query.or(orFilter);
        }

        const { data: books } = await query.order('title', { ascending: true })

        if (books && books.length > 0) {
            jsonLd = {
                '@context': 'https://schema.org',
                '@type': 'ItemList',
                itemListElement: books.map((book, index) => ({
                    '@type': 'ListItem',
                    position: index + 1,
                    item: {
                        '@type': 'Book',
                        name: book.title,
                        author: {
                            '@type': 'Person',
                            name: book.author,
                        },
                        isbn: book.isbn,
                        image: book.image_url,
                        url: `https://checkjari.com/book/${book.id}`,
                    },
                })),
            }
        }
    }

    return (
        <>
            {jsonLd && (
                <script
                    type="application/ld+json"
                    dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
                />
            )}
            <Suspense fallback={<PageLoader />}>
                <BooksPageClient />
            </Suspense>
        </>
    );
}
