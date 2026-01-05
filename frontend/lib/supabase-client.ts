import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export async function getBooksFromSupabase(
    page = 1,
    limit = 24,
    filters?: {
        age?: string;
        category?: string;
        sort?: string;
    }
) {
    let query = supabase
        .from('childbook_items')
        .select('*', { count: 'exact' });

    // 필터 적용
    if (filters?.age) {
        query = query.eq('age', filters.age);
    }
    if (filters?.category && filters.category !== '전체') {
        query = query.eq('category', filters.category);
    }

    // 정렬
    const sortField = filters?.sort || 'pangyo_callno';
    query = query.order(sortField);

    // 페이징
    const start = (page - 1) * limit;
    query = query.range(start, start + limit - 1);

    const { data, count, error } = await query;

    if (error) {
        console.error('Supabase query error:', error);
        throw error;
    }

    return {
        data: data || [],
        total: count || 0,
        total_pages: Math.ceil((count || 0) / limit),
        page,
        limit
    };
}
