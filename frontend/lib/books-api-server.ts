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
        tag?: string;
    }
    client?: SupabaseClient
}

/**
 * SEO/SSG 페이지의 초기 목록을 위한 서버 전용 도서 조회
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

    // 백엔드 목록 API와 동일하게 유효한 판교 청구기호가 있는 책만 표시
    query = query.not('pangyo_callno', 'is', null).neq('pangyo_callno', '없음');

    if (filters?.age) {
        const dbAgeValues = AGE_MAP[filters.age];
        if (dbAgeValues) {
            query = query.in('age', dbAgeValues);
        }
    }
    // category 필터링은 큐레이션 태그 체계로 대체되어 제거됨
    // Curation 필터
    if (filters?.curation) {
        const cleanCuration = filters.curation.replace(/^#/, '').split(/[?&]/)[0].trim();
        if (cleanCuration) {
            const dbCurationTag = resolveDbCurationTag(cleanCuration);
            query = isSpecialTag(dbCurationTag)
                ? query.ilike('curation_tag', `%${dbCurationTag}%`)
                : query.or(buildCurationOrFilter(dbCurationTag));
        }
    }

    // Tag 필터 (교과서 수록도서 학년 태그 등)
    if (filters?.tag) {
        const normalizedTag = filters.tag.replace(/^#/, '');
        query = query.ilike('curation_tag', `%${normalizedTag}%`);
    }

    // 정렬
    let sortField = resolveDefaultSortField(filters?.sort, filters?.curation, filters?.age);

    if (sortField === 'title') {
        query = query.order('title', { ascending: true });
    } else if (sortField === 'confidence_score_desc') {
        query = query.order('confidence_score', { ascending: false });
    } else if (sortField === 'popular' || sortField === 'national_loan_count' || sortField === 'national_loan_count_desc') {
        query = query.order('national_loan_count', { ascending: false, nullsFirst: false });
    } else {
        query = query.order(sortField);
    }

    // 페이징
    const start = (page - 1) * limit;
    query = query.range(start, start + limit - 1);

    const { data, count, error } = await query;

    if (error) {
        console.error('Supabase server query error:', error);
        throw new Error(`Supabase server query failed: ${error.message}`);
    }

    return {
        data: (data as any[]) || [],
        total: count || 0,
        total_pages: Math.ceil((count || 0) / limit),
        page,
        limit
    };
}
