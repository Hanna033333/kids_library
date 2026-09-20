import { MetadataRoute } from 'next'
import { createClient } from '@/lib/supabase'
import { VALID_TAXONOMY } from '@/lib/constants/taxonomy'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    const supabase = createClient()

    // Get all books (not hidden)
    const { data: books } = await supabase
        .from('childbook_items')
        .select('id, updated_at')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .order('id')

    const baseUrl = 'https://www.checkjari.com'

    const routes: MetadataRoute.Sitemap = [
        { url: baseUrl, lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
        // { url: `${baseUrl}/books?curation=winter-vacation`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
        { url: `${baseUrl}/collections/age/0-3`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
        { url: `${baseUrl}/collections/age/4-7`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
        { url: `${baseUrl}/collections/age/8-12`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
        { url: `${baseUrl}/collections/age/teen`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
        { url: `${baseUrl}/collections/research-council`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
        { url: `${baseUrl}/caldecott`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 }
    ]

    // AI curation tags (New semantic path parameter style)
    VALID_TAXONOMY.forEach((item) => {
        routes.push({
            url: `${baseUrl}/collections/curation/${encodeURIComponent(item.slug)}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.9,
        })
        // Fallback backward compatibility
        routes.push({
            url: `${baseUrl}/books?curation=${encodeURIComponent(item.slug)}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.8,
        })
    })

    // Additional specific curations
    const specialCurations = ['winter-vacation', 'summer-vacation', 'research-council', 'caldecott', 'textbook', '교과서수록']
    specialCurations.forEach((curation) => {
        routes.push({
            url: `${baseUrl}/collections/curation/${encodeURIComponent(curation)}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.9,
        })
        // Fallback backward compatibility
        routes.push({
            url: `${baseUrl}/books?curation=${encodeURIComponent(curation)}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.8,
        })
    })

    // 교과서 수록도서 학년별 상세 경로 추가 (SEO 색인 극대화)
    const textbookGrades = ['초등1학년', '초등2학년', '초등3학년', '초등4학년', '초등5학년', '초등6학년']
    textbookGrades.forEach((grade, idx) => {
        // 한글 쿼리
        routes.push({
            url: `${baseUrl}/books?curation=%EA%B5%90%EA%B3%BC%EC%84%9C%EC%88%98%EB%A1%9D&tag=${encodeURIComponent(grade)}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.88,
        })
        // 영문 슬러그 쿼리
        routes.push({
            url: `${baseUrl}/books?curation=textbook&tag=${encodeURIComponent(grade)}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.88,
        })
    })

    // Book detail pages
    if (books) {
        books.forEach((book) => {
            routes.push({
                url: `${baseUrl}/book/${book.id}`,
                lastModified: book.updated_at ? new Date(book.updated_at) : new Date(),
                changeFrequency: 'weekly',
                priority: 0.8,
            })
        })
    }

    return routes
}
