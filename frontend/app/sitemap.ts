import { MetadataRoute } from 'next'
import { createClient } from '@/lib/supabase'
import { VALID_AI_TAGS } from '@/lib/constants/taxonomy'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    const supabase = createClient()

    // Get all books (not hidden)
    const { data: books } = await supabase
        .from('childbook_items')
        .select('id, updated_at')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .order('id')

    const baseUrl = 'https://checkjari.com'

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
    VALID_AI_TAGS.forEach((tag) => {
        routes.push({
            url: `${baseUrl}/collections/curation/${encodeURIComponent(tag)}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.9,
        })
        // Fallback backward compatibility
        routes.push({
            url: `${baseUrl}/books?curation=${encodeURIComponent(tag)}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.8,
        })
    })

    // Additional specific curations
    const specialCurations = ['winter-vacation', 'research-council', 'caldecott']
    specialCurations.forEach((curation) => {
        routes.push({
            url: `${baseUrl}/collections/curation/${curation}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.9,
        })
        // Fallback backward compatibility
        routes.push({
            url: `${baseUrl}/books?curation=${curation}`,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 0.8,
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
