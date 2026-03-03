import { SupabaseClient } from '@supabase/supabase-js'
export async function saveBook(supabase: SupabaseClient, userId: string, bookId: number) {
    const { error } = await supabase
        .from('wishlists')
        .insert([{ user_id: userId, book_id: bookId }])

    if (error) throw error
}

export async function unsaveBook(supabase: SupabaseClient, userId: string, bookId: number) {
    const { error } = await supabase
        .from('wishlists')
        .delete()
        .match({ user_id: userId, book_id: bookId })

    if (error) throw error
}

export async function getSavedBookIds(supabase: SupabaseClient, userId: string): Promise<number[]> {
    const { data, error } = await supabase
        .from('wishlists')
        .select('book_id')
        .eq('user_id', userId)

    if (error) throw error
    return data?.map((item: any) => item.book_id) || []
}
