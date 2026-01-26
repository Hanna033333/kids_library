import { MetadataRoute } from 'next'
import { createClient } from '@/lib/supabase'

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
        { url: `${baseUrl}/collections/age/0-3`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
        { url: `${baseUrl}/collections/age/4-7`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
        { url: `${baseUrl}/collections/age/8-12`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
        { url: `${baseUrl}/collections/age/13+`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
        { url: `${baseUrl}/collections/research-council`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 }
    ]

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
