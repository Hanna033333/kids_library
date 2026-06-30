import { SupabaseClient } from '@supabase/supabase-js'

export async function saveBook(supabase: SupabaseClient, userId: string, bookId: number) {
    if (userId === "00000000-0000-0000-0000-000000000000") {
        console.log('[QA Mock] Skip saving to wishlists DB to avoid FK constraint error');
        return;
    }
    const { error } = await supabase
        .from('wishlists')
        .insert([{ user_id: userId, book_id: bookId }])

    if (error) throw error
}

export async function unsaveBook(supabase: SupabaseClient, userId: string, bookId: number) {
    if (userId === "00000000-0000-0000-0000-000000000000") {
        console.log('[QA Mock] Skip unsaving from wishlists DB');
        return;
    }
    const { error } = await supabase
        .from('wishlists')
        .delete()
        .match({ user_id: userId, book_id: bookId })

    if (error) throw error
}

export async function getSavedBookIds(supabase: SupabaseClient, userId: string): Promise<number[]> {
    if (userId === "00000000-0000-0000-0000-000000000000") {
        return [];
    }
    const { data, error } = await supabase
        .from('wishlists')
        .select('book_id')
        .eq('user_id', userId)

    if (error) throw error
    return data?.map((item: any) => item.book_id) || []
}
