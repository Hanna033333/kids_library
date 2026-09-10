import { createClient } from './supabase'
import { Book } from './types'
import { SupabaseClient } from '@supabase/supabase-js'
import { buildCurationOrFilter, SPECIAL_CURATION_TAGS } from './utils/curation-filter'

/**
 * 도서 카드 렌더링에 필요한 공통 select 필드 (SSOT)
 * 개발 규칙 32번: `book_library_info` 조인은 1:N 오버헤드가 크므로
 * 로그인 상태에서만 `includeLibraryInfo`로 조건부 활성화한다.
 */
const BOOK_FIELDS = 'id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag, national_loan_count'
const LIBRARY_JOIN = 'library_info:book_library_info(library_name, callno)'

function bookSelect(includeLibraryInfo: boolean, extraFields?: string): string {
    const fields = [BOOK_FIELDS, extraFields].filter(Boolean).join(', ')
    return includeLibraryInfo ? `${fields}, ${LIBRARY_JOIN}` : fields
}

/**
 * 노출 가능한 도서만 거르는 공통 기본 쿼리
 * (숨김 처리되지 않았고 표지 이미지가 존재하는 도서)
 */
function visibleBooks(supabase: SupabaseClient, selectFields: string) {
    return supabase
        .from('childbook_items')
        .select(selectFields)
        .or('is_hidden.is.null,is_hidden.eq.false')
        .not('image_url', 'is', null)
        .neq('image_url', '')
}

/** 연도 시작일 기준 경과 주차 (일주일마다 추천 목록이 바뀌는 기준값) */
function getWeekNumber(now: Date = new Date()): number {
    const startOfYear = new Date(now.getFullYear(), 0, 1)
    return Math.floor((now.getTime() - startOfYear.getTime()) / (7 * 24 * 60 * 60 * 1000))
}

/** 연도 시작일 기준 경과 일수 (하루 동안 동일한 랜덤 순서를 유지하는 시드) */
function getDayOfYear(now: Date = new Date()): number {
    const startOfYear = new Date(now.getFullYear(), 0, 1)
    return Math.floor((now.getTime() - startOfYear.getTime()) / (24 * 60 * 60 * 1000))
}

/** 날짜 시드 기반 Fisher-Yates 셔플 (같은 날에는 항상 같은 순서를 보장) */
function seededShuffle<T>(items: T[], seed: number): T[] {
    const seededRandom = (index: number) => {
        const x = Math.sin(seed + index) * 10000
        return x - Math.floor(x)
    }

    const shuffled = [...items]
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(seededRandom(i) * (i + 1))
            ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
    }
    return shuffled
}

/** 'teen' 하위 호환 처리 */
function normalizeAgeGroup(ageGroup: string): string {
    return ageGroup === 'teen' ? '13+' : ageGroup
}

/**
 * 연령별 책 추천 가져오기 (일주일마다 랜덤 변경)
 */
export async function getBooksByAge(ageGroup: string, limit: number = 5, client?: SupabaseClient, includeLibraryInfo: boolean = false): Promise<Book[]> {
    const supabase = client || createClient()

    const normalizedAge = normalizeAgeGroup(ageGroup)
    if (!normalizedAge) return []

    // COUNT 없이 weekNumber 기반 offset 추정 후 단일 쿼리
    // offset이 범위 초과시 fallback(0)으로 1회 더 시도 (최대 왕복 2회지만 대부분 1회)
    const estimatedTotal = 1000 // 충분히 큰 상한값
    const offset = (getWeekNumber() * limit) % estimatedTotal

    const selectFields = bookSelect(includeLibraryInfo)
    const byAge = () => visibleBooks(supabase, selectFields).eq('age', normalizedAge).order('id')

    let { data, error } = await byAge().range(offset, offset + limit - 1)

    if (error) {
        console.error('Error fetching books by age:', error)
        return []
    }

    // offset이 실제 데이터 범위를 초과한 경우 처음부터 재시도
    if (!data || data.length === 0) {
        const fallback = await byAge().range(0, limit - 1)
        if (fallback.error) return []
        data = fallback.data
    }

    const books = (data as any) || []
    // ㄱㄴㄷ 순(제목 오름차순)으로 항상 정렬해서 반환
    return books.sort((a: any, b: any) => a.title.localeCompare(b.title, 'ko'))
}

/**
 * 어린이 도서 연구회 추천 책 가져오기 (일주일마다 랜덤 변경)
 */
export async function getResearchCouncilBooks(limit: number = 5, client?: SupabaseClient, includeLibraryInfo: boolean = false): Promise<Book[]> {
    const supabase = client || createClient()

    // COUNT 쿼리 제거: pool을 한 번에 가져와 클라이언트에서 주차 기반 슬라이싱
    // (DB 왕복 2회 → 1회로 단축)
    const POOL_SIZE = 100 // 어린이도서연구회 64권 이상 커버용

    const { data, error } = await visibleBooks(supabase, bookSelect(includeLibraryInfo))
        .ilike('curation_tag', '%어린이도서연구회%')
        .order('id') // 일관된 정렬
        .limit(POOL_SIZE)

    if (error) {
        console.error('Error fetching research council books:', error)
        return []
    }

    const pool = (data as any) || []
    if (pool.length === 0) return []

    // 클라이언트 슬라이싱: pool 범위 내에서 안전한 offset 계산
    const maxOffset = Math.max(0, pool.length - limit)
    const offset = maxOffset > 0 ? (getWeekNumber() * limit) % (maxOffset + 1) : 0

    return pool.slice(offset, offset + limit)
}

/**
 * 방학 시즌 추천 도서 공통 로직 (매일 랜덤 선정)
 * 정책: 항상 정확히 limit 권 노출 보장 (날짜 시드 기반 랜덤 선택)
 *
 * 매칭 방식은 `SPECIAL_CURATION_TAGS` SSOT를 따른다. 방학 태그는 도서의
 * 주제 태그 뒤에 덧붙는 캠페인 태그이므로(개발 규칙 29의 "첫 번째 태그는
 * 책 내용에 가장 근접한 태그" 원칙에 따라 항상 마지막에 위치) 첫 태그 정밀
 * 매칭 대상이 아니며 `ilike` 부분 일치를 사용한다. 어린이도서연구회 큐레이션과 동일한 규격이다.
 */
async function getSeasonalBooks(
    tag: typeof SPECIAL_CURATION_TAGS[number],
    label: string,
    limit: number,
    client?: SupabaseClient,
    includeLibraryInfo: boolean = false
): Promise<Book[]> {
    const supabase = client || createClient()

    const { data, error } = await visibleBooks(supabase, bookSelect(includeLibraryInfo))
        .ilike('curation_tag', `%${tag}%`)
        .order('id', { ascending: true }) // 먼저 ID로 정렬하여 일관성 확보
        .limit(100) // 충분한 수 가져오기

    if (error) {
        console.error(`Error fetching ${label} books:`, error)
        return []
    }

    if (!data || data.length === 0) {
        return []
    }

    // 날짜 기반 시드로 하루 동안 일관된 랜덤 순서 유지
    const seed = getDayOfYear() * 0.001 // 0~1 사이 값으로 변환
    const shuffled = seededShuffle(data, seed)

    // 정확히 limit 개수만 반환 (기본 7권)
    return shuffled.slice(0, Math.min(limit, shuffled.length)) as any
}

/**
 * 겨울방학 추천 도서 가져오기 (매일 랜덤 7권 선정)
 */
export async function getWinterBooks(limit: number = 7, client?: SupabaseClient, includeLibraryInfo: boolean = false): Promise<Book[]> {
    return getSeasonalBooks('겨울방학2026', 'winter', limit, client, includeLibraryInfo)
}

/**
 * 여름방학 추천 도서 가져오기 (매일 랜덤 7권 선정)
 */
export async function getSummerBooks(limit: number = 7, client?: SupabaseClient, includeLibraryInfo: boolean = false): Promise<Book[]> {
    return getSeasonalBooks('여름방학2026', 'summer', limit, client, includeLibraryInfo)
}

/**
 * 특정 큐레이션 태그가 포함된 책 가져오기 (매칭 방식: 콤마 구분자 포함 여부)
 */
export async function getBooksByTag(tagName: string, limit: number = 7, client?: SupabaseClient, includeLibraryInfo: boolean = false): Promise<Book[]> {
    const supabase = client || createClient()

    // 개발 규칙 29번: 매칭 정확도를 위해 항상 첫 번째 태그와만 매칭한다.
    // 필터 문자열은 curation-filter.ts의 SSOT 헬퍼를 재사용한다.
    const orFilter = buildCurationOrFilter(tagName);

    const selectFields = bookSelect(includeLibraryInfo, 'curation_note, confidence_score')

    const { data, error } = await visibleBooks(supabase, selectFields)
        .or(orFilter)
        .order('confidence_score', { ascending: false }) // 신뢰도 높은 순 우선
        .limit(limit)

    if (error) {
        console.error(`Error fetching books by tag ${tagName}:`, error)
        return []
    }

    return (data as any) || []
}

/**
 * 연령대별 전국 인기 도서 가져오기 (대출수 기준)
 */
export async function getPopularBooksByAge(ageGroup: string, limit: number = 8, client?: SupabaseClient, includeLibraryInfo: boolean = false): Promise<Book[]> {
    const supabase = client || createClient()

    const normalizedAge = normalizeAgeGroup(ageGroup)
    if (!normalizedAge) return []

    const { data, error } = await visibleBooks(supabase, bookSelect(includeLibraryInfo))
        .eq('age', normalizedAge)
        .order('national_loan_count', { ascending: false })
        .limit(limit)

    if (error) {
        console.error('Error fetching popular books by age:', error)
        return []
    }

    return (data as any) || []
}

/**
 * 전체 도서 중 전국 인기 도서 가져오기 (대출수 기준)
 */
export async function getPopularBooksOverall(limit: number = 8, client?: SupabaseClient, includeLibraryInfo: boolean = false): Promise<Book[]> {
    const supabase = client || createClient()

    const { data, error } = await visibleBooks(supabase, bookSelect(includeLibraryInfo))
        .order('national_loan_count', { ascending: false })
        .limit(limit)

    if (error) {
        console.error('Error fetching popular books overall:', error)
        return []
    }

    return (data as any) || []
}

/**
 * 저자 필드에서 주 저자명 정제 추출 헬퍼 (예: "백희나 글, 그림" -> "백희나")
 */
export function cleanAuthorName(authorStr?: string | null): string {
    if (!authorStr) return ''
    const firstPart = authorStr.split(/[,|/│]/)[0].trim()
    const cleaned = firstPart.replace(/\s*(글|그림|지음|저|옮김|역|글·그림|글\/그림|원작).*$/g, '').trim()
    return cleaned || firstPart
}

/**
 * 동일 저자/그림작가의 다른 추천 도서 가져오기
 */
export async function getBooksByAuthor(authorName: string, excludeBookId?: number, limit: number = 7, client?: SupabaseClient): Promise<Book[]> {
    const supabase = client || createClient()
    const mainAuthor = cleanAuthorName(authorName)
    if (!mainAuthor) return []

    let query = visibleBooks(supabase, bookSelect(false))
        .ilike('author', `%${mainAuthor}%`)

    if (excludeBookId) {
        query = query.neq('id', excludeBookId)
    }

    const { data, error } = await query.order('id', { ascending: false }).limit(limit)

    if (error) {
        console.error('Error fetching books by author:', error)
        return []
    }

    return (data as any) || []
}
