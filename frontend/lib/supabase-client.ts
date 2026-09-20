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
        q?: string;
        age?: string;
        sort?: string;
        curation?: string;
        tag?: string;
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

    // 검색어 필터 (제목, 저자, 출판사, 큐레이션 태그 검색)
    if (filters?.q) {
        const cleanQ = filters.q.trim();
        if (cleanQ) {
            query = query.or(`title.ilike.%${cleanQ}%,author.ilike.%${cleanQ}%,publisher.ilike.%${cleanQ}%,curation_tag.ilike.%${cleanQ}%`);
        }
    }

    // 연령 필터 — DB 표준화 및 레거시 포맷(8세부터, 7세부터 등) 다중 매칭 지원
    if (filters?.age) {
        const rawAge = filters.age === 'teen' ? '13+' : filters.age;
        if (rawAge === '8-12' || rawAge.includes('8세') || rawAge.includes('9세') || rawAge.includes('초등')) {
            query = query.or('age.eq.8-12,age.eq.8세부터,age.eq.9세부터,age.eq.8~12세');
        } else if (rawAge === '4-7' || rawAge.includes('4세') || rawAge.includes('5세') || rawAge.includes('6세') || rawAge.includes('7세')) {
            query = query.or('age.eq.4-7,age.eq.5세부터,age.eq.7세부터,age.eq.4~7세');
        } else if (rawAge === '0-3' || rawAge.includes('0세') || rawAge.includes('1세') || rawAge.includes('2세') || rawAge.includes('3세')) {
            query = query.or('age.eq.0-3,age.eq.0~3세,age.eq.0-2세,age.eq.3세부터');
        } else {
            query = query.eq('age', rawAge);
        }
    }
    // category는 제거됨 (큐레이션 태그 체계로 대체)
    // Curation 필터 — ?나 & 쿼리스트링 오염 안전 정제
    if (filters?.curation) {
        const cleanCuration = filters.curation.replace(/^#/, '').split(/[?&]/)[0].trim();
        if (cleanCuration) {
            const dbCurationTag = resolveDbCurationTag(cleanCuration);
            query = query.ilike('curation_tag', `%${dbCurationTag}%`);
        }
    }

    // Tag 필터 (교과서 수록도서 학년 태그 등)
    if (filters?.tag) {
        const normalizedTag = filters.tag.replace(/^#/, '');
        query = query.ilike('curation_tag', `%${normalizedTag}%`);
    }

    // 정렬
    let sortField = resolveDefaultSortField(filters?.sort, filters?.curation, filters?.age);

    if (sortField === 'confidence_score_desc') {
        query = query.order('confidence_score', { ascending: false });
    } else if (sortField === 'title') {
        query = query.order('title', { ascending: true });
    } else if (sortField === 'popular' || sortField === 'national_loan_count' || sortField === 'national_loan_count_desc') {
        query = query.order('national_loan_count', { ascending: false, nullsFirst: false });
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
