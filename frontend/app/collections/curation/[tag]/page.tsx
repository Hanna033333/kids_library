import HomeClient from "@/components/HomeClient";
import { Metadata } from 'next'
import { VALID_TAXONOMY, VALID_AI_TAGS } from '@/lib/constants/taxonomy'
import { createClient } from '@/lib/supabase'
import { Suspense } from 'react'
import { PageLoader } from '@/components/ui/PageLoader'

interface Props {
    params: Promise<{ tag: string }>
}

export const revalidate = 86400 // 24시간마다 백그라운드 재검증 (ISR)
export const dynamicParams = true

// 빌드 타임에 모든 AI 큐레이션 페이지와 겨울방학, 칼데콧, 어린이도서연구회 큐레이션을 정적 파일로 초고속 생성
export async function generateStaticParams() {
    const specialCurations = ['winter-vacation', 'research-council', 'caldecott']
    const aiSlugs = VALID_TAXONOMY.map(item => item.slug)
    const allTags = [...aiSlugs, ...specialCurations]
    
    return allTags.map((tag) => ({
        tag: encodeURIComponent(tag),
    }))
}

// 큐레이션별 메타데이터 생성 (롱테일 키워드 검색 엔진 최적화)
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { tag: rawTag } = await params
    const curation = rawTag ? decodeURIComponent(rawTag) : ''

    const matchedTaxonomy = VALID_TAXONOMY.find(item => item.slug === curation || item.tag === curation);
    const curationTag = matchedTaxonomy ? matchedTaxonomy.tag : curation;

    let title = '책자리 - 우리 아이 상황별 맞춤 도서 큐레이션'
    let description = '어떤 책을 읽혀야 할지 고민되는 부모님을 위해! 아이의 연령과 정서적 상황(잠자리, 사회성, 감정 발달 등)에 딱 맞는 전문가 엄선 도서 큐레이션 목록과 전국 도서관 소장 정보 및 바로 구매를 확인해 보세요.'
    let keywords = '어린이 도서 추천, 아동 도서 검색, 도서 큐레이션, 어린이 정서 발달, 상황별 그림책, 도서 대출 확인'

    if (curationTag === 'winter-vacation' || curationTag === '겨울방학') {
        title = '스마트폰만 보는 아이, 방학 때 뭐 읽힐까요? | 책자리 겨울방학 추천도서'
        description = '사서가 직접 뽑았다! 실패 없는 겨울방학 추천도서 리스트를 도서관에서 바로 대출하세요. 초등학생 필독서부터 인기 베스트까지 한눈에 확인하세요.'
        keywords = '겨울방학 독서 숙제, 초등 겨울방학 추천도서, 문해력 향상 도서, 독서록 쓰기 좋은 책, 학년별 추천 도서, 사서 추천'
    } else if (curationTag === 'research-council' || curationTag === '어린이도서연구회') {
        title = "전문가가 보증하는 '찐' 필독서 모음 | 어린이도서연구회 추천도서 - 책자리"
        description = '엄마표 독서 고민 끝! 어린이 도서 연구회가 엄선한 필독서를 도서관에서 바로 대출하세요. 전문가 추천 베스트 어린이 책 리스트를 지금 확인하세요.'
        keywords = '어린이 도서 연구회, 전문가 추천 도서, 사서 추천, 어린이 필독서, 베스트 어린이 책, 권장도서'
    } else if (curationTag === 'caldecott') {
        title = "2000-2026 칼데콧 수상작 | 세계 최고의 어린이 그림책 리스트 - 책자리"
        description = '2000년부터 2026년까지 칼데콧 메달을 수상한 세계 최고의 어린이 그림책 목록입니다. 전국 도서관 소장 여부와 실시간 대출 정보를 확인하고 바로 읽혀보세요.'
        keywords = '칼데콧상, Caldecott Medal, 어린이 그림책, 수상작, 추천 도서, 전국 도서관 대출, 그림책 노벨상'
    } else if (matchedTaxonomy) {
        title = `[${matchedTaxonomy.tag} 그림책 추천] ${matchedTaxonomy.subtitle} | ${matchedTaxonomy.title} - 책자리`
        description = `"${matchedTaxonomy.subtitle}" 우리 아이의 마음과 정서에 꼭 맞는 '${matchedTaxonomy.tag}' 엄선 그림책 리스트! 주변 도서관 소장 상태, 대출 정보 및 교보문고 바로 구매 링크를 만나보세요.`
        keywords = `${matchedTaxonomy.tag}, ${matchedTaxonomy.title}, 그림책 큐레이션, 그림책 추천, 어린이 도서, 책자리, 부모 필독서, 정서 발달`
    }

    return {
        title,
        description,
        keywords,
        alternates: {
            canonical: `/collections/curation/${encodeURIComponent(curation)}`
        },
        openGraph: {
            title,
            description,
            type: 'website',
            url: `https://checkjari.com/collections/curation/${encodeURIComponent(curation)}`
        },
        twitter: {
            card: 'summary_large_image',
            title,
            description
        }
    }
}

// 큐레이션 랜딩 페이지 컴포넌트
export default async function CurationPage({ params }: Props) {
    const { tag: rawTag } = await params
    const curation = rawTag ? decodeURIComponent(rawTag) : ''

    const matchedTaxonomy = VALID_TAXONOMY.find(item => item.slug === curation || item.tag === curation);
    const curationTag = matchedTaxonomy ? matchedTaxonomy.tag : curation;

    let jsonLd = null;

    // Supabase 직접 조회를 통해 구조화된 데이터(JSON-LD ItemList) 생성 -> 봇 수집 극대화
    const isKnownCuration = ['winter-vacation', 'research-council', 'caldecott'].includes(curationTag) || 
                            VALID_AI_TAGS.includes(curationTag);
    if (curationTag && isKnownCuration) {
        const supabase = createClient()
        let query = supabase
            .from('childbook_items')
            .select('id, title, author, isbn, image_url')
            .or('is_hidden.is.null,is_hidden.eq.false')

        const SPECIAL_TAGS = ['winter-vacation', 'research-council', 'caldecott', '겨울방학2026', '어린이도서연구회'];
        if (SPECIAL_TAGS.includes(curationTag)) {
            query = query.ilike('curation_tag', `%${curationTag}%`);
        } else {
            const orFilter = `curation_tag.eq."${curationTag}",curation_tag.like."${curationTag},%",curation_tag.eq."#${curationTag}",curation_tag.like."#${curationTag},%"`;
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
                            name: book.author || '저자 미상',
                        },
                        isbn: book.isbn || '',
                        image: book.image_url || '',
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
            
            {/* 1번 전략: 검색 봇이 100% 긁어갈 수 있는 정적 텍스트 정보 노출 */}
            <article className="hidden" aria-hidden="true" style={{ display: 'none' }}>
                <h1>책자리 {curationTag} 맞춤 도서 추천 컬렉션</h1>
                <p>어떤 책을 읽혀야 할지 모르는 부모님을 위한 특별 큐레이션</p>
                {jsonLd && (
                    <ul>
                        {(jsonLd as any).itemListElement.map((el: any) => (
                            <li key={el.item.url}>
                                <a href={el.item.url}>{el.item.name}</a> - 저자: {el.item.author.name}
                            </li>
                        ))}
                    </ul>
                )}
            </article>

            {/* useSearchParams() 사용에 따른 Next.js CSR Bailout 에러 차단을 위해 Suspense Boundary로 감싸기 */}
            <Suspense fallback={<PageLoader />}>
                <HomeClient overrideCuration={curationTag} />
            </Suspense>
        </>
    );
}
