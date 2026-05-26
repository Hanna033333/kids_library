import HomeClient from "@/components/HomeClient";
import { Metadata } from 'next'
import { VALID_TAXONOMY, VALID_AI_TAGS } from '@/lib/constants/taxonomy'

interface Props {
    searchParams: { age?: string; curation?: string; category?: string; q?: string }
}

export async function generateMetadata({ searchParams }: Props): Promise<Metadata> {
    const { age: rawAge, curation: rawCuration, q } = searchParams
    const curation = rawCuration ? decodeURIComponent(rawCuration) : undefined
    const age = rawAge ? decodeURIComponent(rawAge) : undefined

    let title = '책자리 - 우리 아이 맞춤 도서관 책 찾기'
    let description = '어떤 책을 읽혀야 할지 고민되는 부모님을 위해! 로그인 없이 3초 만에 주변 도서관 책 소장 여부와 대출 가능 현황, 청구기호까지 한눈에 확인하세요.'
    let keywords = '어린이 도서 추천, 아동 도서 검색, 도서관 청구기호, 도서 대출 확인, 판교도서관'

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
        description = '2000년부터 2026년까지 칼데콧 메달을 수상한 세계 최고의 어린이 그림책 목록입니다. 판교도서관 청구기호와 대출 정보를 확인하고 바로 읽혀보세요.'
        keywords = '칼데콧상, Caldecott Medal, 어린이 그림책, 수상작, 추천 도서, 판교도서관, 그림책 노벨상'
    } else if (matchedTaxonomy) {
        title = `${matchedTaxonomy.subtitle} | ${matchedTaxonomy.title} - 책자리`
        description = `"${matchedTaxonomy.subtitle}" 우리 아이의 마음과 정서에 꼭 맞는 '${matchedTaxonomy.tag}' 엄선 그림책 리스트! 주변 도서관 대출 가능 여부와 위치(청구기호)를 바로 확인하세요.`
        keywords = `${matchedTaxonomy.tag}, ${matchedTaxonomy.title}, 그림책 큐레이션, 그림책 추천, 어린이 도서, 책자리, 부모 필독서`
    } else if (age) {
        // 다양한 연령대 입력(예: 0-3, 0-2세, 3-4세, 4-7, 5-7세 등)을 지원하기 위해 정규화
        const ageClean = age.replace(/\s+/g, '');
        if (ageClean === '0-3' || ageClean === '0-2세' || ageClean.includes('0세') || ageClean.includes('1세') || ageClean.includes('2세') || ageClean.includes('3세')) {
            title = '0~3세 영유아 그림책 추천 | 3세 책 추천 단권 - 책자리'
            description = '전집 고민 그만! 0세, 1세, 2세, 3세 우리 아기 신체 발달과 감각 자극에 딱 맞는 도서관 추천 그림책 리스트를 3초 만에 만나보세요.'
            keywords = '3세 그림책, 3세 책 추천 단권, 0-3세 추천 도서, 영유아 그림책, 아기2살 책종류, 3-4개월 아기 책추천'
        } else if (ageClean === '4-7' || ageClean === '3-4세' || ageClean === '5-7세' || ageClean.includes('4세') || ageClean.includes('5세') || ageClean.includes('6세') || ageClean.includes('7세') || ageClean.includes('유치원')) {
            title = '7세 책 추천 리스트 | 유치원생 필독도서 & 그림책 추천 - 책자리'
            description = '4세, 5세, 6세, 7세 유치원생이 읽기 좋은 예쁜 그림책과 추천 도서 리스트! 주변 도서관 청구기호와 대출 정보를 확인하고 바로 대출하세요.'
            keywords = '7세 책 추천 리스트, 유치원생 필독도서, 유치원생 책 추천, 7세 추천도서 그림책, 7세 동화책 추천순, 주변 도서관 책 검색'
        } else if (ageClean === '8-12' || ageClean === '8-13세' || ageClean.includes('8세') || ageClean.includes('9세') || ageClean.includes('10세') || ageClean.includes('11세') || ageClean.includes('12세') || ageClean.includes('초등')) {
            title = '8~12세 초등학생 필독서 추천 | 학년별 베스트셀러 - 책자리'
            description = '초등학생 자녀의 어휘력과 자존감을 키워줄 필독 동화책 목록! 주변 도서관 청구기호와 대출 가능 상태를 지금 확인하세요.'
            keywords = '8세 스테디셀러 동화, 초등학생 필독서, 초등 추천 도서, 학년별 권장도서, 사서 추천'
        } else {
            title = `우리 아이 나이에 딱! ${age} 맞춤 도서 - 책자리`
            description = `우리 아이 ${age} 연령대 발달 단계와 관심사에 딱 맞춘 추천 그림책과 동화책 리스트! 도서관에서 기다리지 말고 3초 만에 확인하세요.`
            keywords = `${age} 추천 도서, 어린이 책 추천, 학년별 권장도서, 책자리`
        }
    } else if (q) {
        title = `"${q}" - 도서관에 있을까? 3초 만에 검색 | 책자리`
        description = `도서관 가기 전 헛걸음 방지! "${q}" 도서의 주변 도서관 대출 가능 여부, 소장 상태 및 청구기호를 실시간으로 빠르게 확인하세요.`
        keywords = `${q}, 주변 도서관 책 검색, 주변 도서관 책찾기, 도서관 청구기호 확인, 책자리`
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
        const { data: books } = await supabase
            .from('childbook_items')
            .select('id, title, author, isbn, image_url')
            .ilike('curation_tag', `%${curation}%`)
            .or('is_hidden.is.null,is_hidden.eq.false')
            .order('title', { ascending: true })

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
            <HomeClient />
        </>
    );
}
