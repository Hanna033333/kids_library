import { createClient } from './supabase'
import { Book } from './types'
import { SupabaseClient } from '@supabase/supabase-js'
import { AGE_MAP } from './constants/age-map'

/**
 * 연령별 책 추천 가져오기 (일주일마다 랜덤 변경)
 */
export async function getBooksByAge(ageGroup: string, limit: number = 5, client?: SupabaseClient): Promise<Book[]> {
    const supabase = client || createClient()

    const ageValues = AGE_MAP[ageGroup] || []
    if (ageValues.length === 0) return []

    // 현재 주차 계산 (일주일마다 바뀜)
    const now = new Date()
    const startOfYear = new Date(now.getFullYear(), 0, 1)
    const weekNumber = Math.floor((now.getTime() - startOfYear.getTime()) / (7 * 24 * 60 * 60 * 1000))

    // COUNT 없이 weekNumber 기반 offset 추정 후 단일 쿼리
    // offset이 범위 초과시 fallback(0)으로 1회 더 시도 (최대 왕복 2회지만 대부분 1회)
    const estimatedTotal = 1000 // 충분히 큰 상한값
    const offset = (weekNumber * limit) % estimatedTotal

    const fetchBooks = async (start: number) => supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, national_loan_count, library_info:book_library_info(library_name, callno)')
        .in('age', ageValues)
        .or('is_hidden.is.null,is_hidden.eq.false')
        .not('image_url', 'is', null)
        .neq('image_url', '')
        .order('id')
        .range(start, start + limit - 1)

    let { data, error } = await fetchBooks(offset)

    if (error) {
        console.error('Error fetching books by age:', error)
        return []
    }

    // offset이 실제 데이터 범위를 초과한 경우 처음부터 재시도
    if (!data || data.length === 0) {
        const fallback = await fetchBooks(0)
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
export async function getResearchCouncilBooks(limit: number = 5, client?: SupabaseClient): Promise<Book[]> {
    const supabase = client || createClient()

    // COUNT 쿼리 제거: pool을 한 번에 가져와 클라이언트에서 주차 기반 슬라이싱
    // (DB 왕복 2회 → 1회로 단축)
    const POOL_SIZE = 100 // 어린이도서연구회 64권 이상 커버용
    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag, national_loan_count, library_info:book_library_info(library_name, callno)')
        .eq('curation_tag', '어린이도서연구회')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .not('image_url', 'is', null)
        .neq('image_url', '')
        .order('id') // 일관된 정렬
        .limit(POOL_SIZE)

    if (error) {
        console.error('Error fetching research council books:', error)
        return []
    }

    const pool = (data as any) || []
    if (pool.length === 0) return []

    // 현재 주차 계산 (일주일마다 바뀜)
    const now = new Date()
    const startOfYear = new Date(now.getFullYear(), 0, 1)
    const weekNumber = Math.floor((now.getTime() - startOfYear.getTime()) / (7 * 24 * 60 * 60 * 1000))

    // 클라이언트 슬라이싱: pool 범위 내에서 안전한 offset 계산
    const maxOffset = Math.max(0, pool.length - limit)
    const offset = maxOffset > 0 ? (weekNumber * limit) % (maxOffset + 1) : 0

    return pool.slice(offset, offset + limit)
}


/**
 * 겨울방학 추천 도서 가져오기 (매일 랜덤 7권 선정)
 * 정책: 항상 정확히 7권 노출 보장 (랜덤 선택)
 */
export async function getWinterBooks(limit: number = 7, client?: SupabaseClient): Promise<Book[]> {
    const supabase = client || createClient()

    // 날짜 기반 시드로 하루 동안 일관된 랜덤 순서 유지
    const now = new Date()
    const dayOfYear = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 1).getTime()) / (24 * 60 * 60 * 1000))
    const seed = dayOfYear * 0.001 // 0~1 사이 값으로 변환

    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag, national_loan_count, library_info:book_library_info(library_name, callno)')
        .eq('curation_tag', '겨울방학2026')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .not('image_url', 'is', null)
        .neq('image_url', '')
        // PostgreSQL RANDOM() 함수로 랜덤 정렬 (시드 기반)
        .order('id', { ascending: true }) // 먼저 ID로 정렬하여 일관성 확보
        .limit(100) // 충분한 수 가져오기

    if (error) {
        console.error('Error fetching winter books:', error)
        return []
    }

    if (!data || data.length === 0) {
        return []
    }

    // 클라이언트 사이드에서 시드 기반 랜덤 선택
    const seededRandom = (index: number) => {
        // Simple seeded random using day + index
        const x = Math.sin(seed + index) * 10000
        return x - Math.floor(x)
    }

    // Fisher-Yates shuffle with seeded random
    const shuffled = [...data]
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(seededRandom(i) * (i + 1))
            ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
    }

    // 정확히 limit 개수만 반환 (기본 7권)
    return shuffled.slice(0, Math.min(limit, shuffled.length)) as any
}

/**
 * 특정 큐레이션 태그가 포함된 책 가져오기 (매칭 방식: 콤마 구분자 포함 여부)
 */
export async function getBooksByTag(tagName: string, limit: number = 7, client?: SupabaseClient): Promise<Book[]> {
    const supabase = client || createClient()

    const orFilter = `curation_tag.eq."${tagName}",curation_tag.like."${tagName},%",curation_tag.eq."#${tagName}",curation_tag.like."#${tagName},%"`;

    const { data, error } = await supabase
        .from('childbook_items')
        .select(`
            id, title, author, publisher, category, age, pangyo_callno, image_url, 
            curation_tag, curation_note, confidence_score, national_loan_count,
            library_info:book_library_info(library_name, callno)
        `)
        .or(orFilter)
        .or('is_hidden.is.null,is_hidden.eq.false')
        .not('image_url', 'is', null)
        .neq('image_url', '')
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
export async function getPopularBooksByAge(ageGroup: string, limit: number = 8, client?: SupabaseClient): Promise<Book[]> {
    const supabase = client || createClient()

    const ageValues = AGE_MAP[ageGroup] || []
    if (ageValues.length === 0) return []

    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, national_loan_count, library_info:book_library_info(library_name, callno)')
        .in('age', ageValues)
        .or('is_hidden.is.null,is_hidden.eq.false')
        .not('image_url', 'is', null)
        .neq('image_url', '')
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
export async function getPopularBooksOverall(limit: number = 8, client?: SupabaseClient): Promise<Book[]> {
    const supabase = client || createClient()

    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, national_loan_count, library_info:book_library_info(library_name, callno)')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .not('image_url', 'is', null)
        .neq('image_url', '')
        .order('national_loan_count', { ascending: false })
        .limit(limit)

    if (error) {
        console.error('Error fetching popular books overall:', error)
        return []
    }

    return (data as any) || []
}

