import { createClient } from '@supabase/supabase-js';
import { AGE_MAP } from './constants/age-map';
import { resolveDbCurationTag, isSpecialTag, buildCurationOrFilter, resolveDefaultSortField } from './utils/curation-filter';

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
        .select('*, library_info:book_library_info(library_name, callno)', { count: 'exact' });

    // is_hidden 필터 (컬럼이 있으면 적용)
    try {
        query = query.or('is_hidden.is.null,is_hidden.eq.false');
    } catch (e) {
        // is_hidden 컬럼이 없으면 무시
    }

    // 필터 적용
    if (filters?.age) {
        const dbAgeValues = AGE_MAP[filters.age];
        if (dbAgeValues) {
            query = query.in('age', dbAgeValues);
        }
    }
    if (filters?.category && filters.category !== '전체') {
        query = query.eq('category', filters.category);
    }
    // Curation 필터
    if (filters?.curation) {
        const dbCurationTag = resolveDbCurationTag(filters.curation);
        if (isSpecialTag(dbCurationTag)) {
            query = query.ilike('curation_tag', `%${dbCurationTag}%`);
        } else {
            query = query.or(buildCurationOrFilter(dbCurationTag));
        }
    }

    // 정렬
    let sortField = resolveDefaultSortField(filters?.sort, filters?.curation, filters?.age);

    if (sortField === 'confidence_score_desc') {
        query = query.order('confidence_score', { ascending: false });
    } else if (sortField === 'title') {
        query = query.order('title', { ascending: true });
    } else {
        query = query.order(sortField);
    }

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
