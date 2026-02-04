import { createClient } from './supabase'
import { Book } from './types'
import { SupabaseClient } from '@supabase/supabase-js'

/**
 * 칼데콧 수상작 가져오기 (2000-2026)
 * curation_tag = 'caldecott'인 도서 조회
 */
export async function getCaldecottBooks(client?: SupabaseClient): Promise<Book[]> {
    const supabase = client || createClient()

    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, isbn, curation_tag, library_info:book_library_info(library_name, callno)')
        .eq('curation_tag', 'caldecott')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .order('title', { ascending: true })

    if (error) {
        console.error('Error fetching Caldecott books:', error)
        return []
    }

    return (data as any) || []
}
