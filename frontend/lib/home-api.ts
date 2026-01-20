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
        '13+': ['13세부터', '16세부터']
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
 * 겨울방학 추천 도서 가져오기 (매주 8권씩 로테이션)
 * 총 40권 가정: 5주 주기로 순환
 */
export async function getWinterBooks(limit: number = 7): Promise<Book[]> {
    const supabase = createClient()

    // 현재 주차 계산
    const now = new Date()
    const startOfYear = new Date(now.getFullYear(), 0, 1)
    const weekNumber = Math.floor((now.getTime() - startOfYear.getTime()) / (7 * 24 * 60 * 60 * 1000))

    // 40권 중 매주 다른 책 노출 (offset)
    // weekNumber * limit을 하면 매주 limit만큼 이동
    // 40권 넘어가면 다시 0부터 (modulo)
    const totalBooks = 40
    const offset = (weekNumber * limit) % totalBooks

    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag, library_info:book_library_info(library_name, callno)')
        .eq('curation_tag', '겨울방학2026')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .order('id') // ID 순서대로 정렬하여 로테이션 일관성 유지
        .range(offset, offset + limit - 1)

    if (error) {
        console.error('Error fetching winter books:', error)
        return []
    }

    return (data as any) || []
}
