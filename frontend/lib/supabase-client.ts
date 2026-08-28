import { createClient } from '@supabase/supabase-js';
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
        sort?: string;
        curation?: string;
    },
    includeLibraryInfo: boolean = false
) {
    const selectFields = includeLibraryInfo
        ? '*, library_info:book_library_info(library_name, callno)'
        : '*';

    let query = supabase
        .from('childbook_items')
        .select(selectFields, { count: 'exact' });

    // is_hidden 필터 (컬럼이 있으면 적용)
    try {
        query = query.or('is_hidden.is.null,is_hidden.eq.false');
    } catch (e) {
        // is_hidden 컬럼이 없으면 무시
    }

    // pangyo_callno가 있는 책만 표시 (백엔드 services/search.py와 동일한 필터).
    // 이 필터가 빠져 있으면 검색어를 입력했을 때(백엔드 /api/books/search 경유)와
    // 입력하지 않았을 때(이 함수 경유) 노출되는 도서 목록이 서로 달라집니다.
    query = query.not('pangyo_callno', 'is', null).neq('pangyo_callno', '없음');

    // 연령 필터 — DB 표준화 후 단순 .eq() 쿼리
    if (filters?.age) {
        const ageKey = filters.age === 'teen' ? '13+' : filters.age;
        query = query.eq('age', ageKey);
    }
    // category는 제거됨 (큐레이션 태그 체계로 대체)
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

    const { data, count, error } = await (query as any);

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
