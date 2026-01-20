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
        curation?: string;
    }
) {
    let query = supabase
        .from('childbook_items')
        .select('*', { count: 'exact' });

    // is_hidden 필터 (컬럼이 있으면 적용)
    try {
        query = query.or('is_hidden.is.null,is_hidden.eq.false');
    } catch (e) {
        // is_hidden 컬럼이 없으면 무시
    }

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
    // Curation 필터 (겨울방학 등)
    if (filters?.curation) {
        // URL param 값을 DB tag 값으로 매핑
        const curationMapping: Record<string, string> = {
            '겨울방학': '겨울방학2026',
            '어린이도서연구회': '어린이도서연구회'
        };
        const dbCurationTag = curationMapping[filters.curation] || filters.curation;
        query = query.eq('curation_tag', dbCurationTag);
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
