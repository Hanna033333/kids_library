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
        // 나이 필터 매핑: 프론트엔드 값 → DB 값
        const ageMapping: Record<string, string[]> = {
            '0-3': ['0세부터', '3세부터'],
            '4-7': ['5세부터', '7세부터'],
            '8-12': ['9세부터', '11세부터'],
            '13+': ['13세부터', '16세부터']
        };

        const dbAgeValues = ageMapping[filters.age];
        if (dbAgeValues) {
            query = query.in('age', dbAgeValues);
        }
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
