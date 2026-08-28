import { createClient } from './supabase-server'
import { Book } from './types'
import { SupabaseClient } from '@supabase/supabase-js'
import { AGE_MAP } from './constants/age-map'
import { resolveDbCurationTag, isSpecialTag, buildCurationOrFilter, resolveDefaultSortField } from './utils/curation-filter'

interface FetchBooksParams {
    page?: number;
    limit?: number;
    filters?: {
        age?: string;
        category?: string;
        sort?: string;
        curation?: string;
    }
    client?: SupabaseClient
}

/**
 * Server-side equivalent of getBooksFromSupabase
 */
export async function getBooksFromServer({
    page = 1,
    limit = 24,
    filters,
    client
}: FetchBooksParams) {
    const supabase = client || createClient()

    let query = supabase
        .from('childbook_items')
        .select('*', { count: 'exact' });

    // is_hidden 필터 (컬럼이 있으면 적용)
    // Note: On server side we assume column exists or Supabase handles it gracefully, 
    // but .or syntax is safer to just apply always.
    query = query.or('is_hidden.is.null,is_hidden.eq.false');

    // pangyo_callno가 있는 책만 표시 (백엔드 services/search.py, lib/supabase-client.ts와 동일한 필터)
    query = query.not('pangyo_callno', 'is', null).neq('pangyo_callno', '없음');

    if (filters?.age) {
        const dbAgeValues = AGE_MAP[filters.age];
        if (dbAgeValues) {
            query = query.in('age', dbAgeValues);
        }
    }
    // category 필터링은 큐레이션 태그 체계로 대체되어 제거됨 (services/search.py, supabase-client.ts와 동일)
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

    if (sortField === 'title') {
        query = query.order('title', { ascending: true });
    } else if (sortField === 'confidence_score_desc') {
        query = query.order('confidence_score', { ascending: false });
    } else {
        query = query.order(sortField);
    }

    // 페이징
    const start = (page - 1) * limit;
    query = query.range(start, start + limit - 1);

    const { data, count, error } = await query;

    if (error) {
        console.error('Supabase server query error:', error);
        return { data: [], total: 0, total_pages: 0, page, limit };
    }

    return {
        data: (data as any[]) || [],
        total: count || 0,
        total_pages: Math.ceil((count || 0) / limit),
        page,
        limit
    };
}
