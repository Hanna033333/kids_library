import { MetadataRoute } from 'next'
import { createClient } from '@/lib/supabase-server'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    const supabase = createClient()

    // Get all books (not hidden)
    const { data: books } = await supabase
        .from('childbook_items')
        .select('id, updated_at')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .order('id')

    const baseUrl = 'https://bookbangu.com'

    // Main page
    const routes: MetadataRoute.Sitemap = [
        {
            url: baseUrl,
            lastModified: new Date(),
            changeFrequency: 'daily',
            priority: 1,
        },
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
