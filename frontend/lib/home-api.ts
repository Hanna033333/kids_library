import { createClient } from './supabase'
import { Book } from './types'

/**
 * 연령별 책 추천 가져오기 (일주일마다 랜덤 변경)
 */
export async function getBooksByAge(ageGroup: string, limit: number = 5): Promise<Book[]> {
    const supabase = createClient()

    // 연령 그룹 매핑
    const ageMap: Record<string, string[]> = {
        '0-3': ['0세부터', '3세부터'],
        '4-7': ['5세부터', '7세부터'],
        '8-12': ['9세부터', '11세부터'],
        'teen': ['13세부터', '16세부터']
    }

    const ageValues = ageMap[ageGroup] || []

    if (ageValues.length === 0) {
        return []
    }

    // 현재 주차 계산 (일주일마다 바뀜)
    const now = new Date()
    const startOfYear = new Date(now.getFullYear(), 0, 1)
    const weekNumber = Math.floor((now.getTime() - startOfYear.getTime()) / (7 * 24 * 60 * 60 * 1000))

    // 주차를 offset으로 사용 (매주 다른 책 선택)
    const offset = (weekNumber * 5) % 100 // 100개 범위 내에서 순환

    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, library_info:book_library_info(library_name, callno)')
        .in('age', ageValues)
        .or('is_hidden.is.null,is_hidden.eq.false')
        .order('id') // 일관된 정렬
        .range(offset, offset + limit - 1)

    if (error) {
        console.error('Error fetching books by age:', error)
        return []
    }

    return (data as any) || []
}

/**
 * 어린이 도서 연구회 추천 책 가져오기 (일주일마다 랜덤 변경)
 */
export async function getResearchCouncilBooks(limit: number = 5): Promise<Book[]> {
    const supabase = createClient()

    // 현재 주차 계산 (일주일마다 바뀜)
    const now = new Date()
    const startOfYear = new Date(now.getFullYear(), 0, 1)
    const weekNumber = Math.floor((now.getTime() - startOfYear.getTime()) / (7 * 24 * 60 * 60 * 1000))

    // 주차를 offset으로 사용 (매주 다른 책 선택)
    const offset = (weekNumber * 5) % 50 // 50개 범위 내에서 순환

    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag, library_info:book_library_info(library_name, callno)')
        .eq('curation_tag', '어린이도서연구회')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .order('id') // 일관된 정렬
        .range(offset, offset + limit - 1)

    if (error) {
        console.error('Error fetching research council books:', error)
        return []
    }

    return (data as any) || []
}


/**
 * 겨울방학 추천 도서 가져오기 (매일 랜덤 7권 선정)
 * 정책: 항상 정확히 7권 노출 보장 (랜덤 선택)
 */
export async function getWinterBooks(limit: number = 7): Promise<Book[]> {
    const supabase = createClient()

    // 날짜 기반 시드로 하루 동안 일관된 랜덤 순서 유지
    const now = new Date()
    const dayOfYear = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 1).getTime()) / (24 * 60 * 60 * 1000))
    const seed = dayOfYear * 0.001 // 0~1 사이 값으로 변환

    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag, library_info:book_library_info(library_name, callno)')
        .eq('curation_tag', '겨울방학2026')
        .or('is_hidden.is.null,is_hidden.eq.false')
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
