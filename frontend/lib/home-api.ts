import { createClient } from './supabase'

export interface Book {
    id: number
    title: string
    author: string
    publisher: string
    category: string
    age: string
    pangyo_callno: string
    image_url: string
    curation_tag?: string
}

/**
 * 연령별 책 추천 가져오기
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

    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url')
        .in('age', ageValues)
        .or('is_hidden.is.null,is_hidden.eq.false')
        .limit(limit)

    if (error) {
        console.error('Error fetching books by age:', error)
        return []
    }

    return data || []
}

/**
 * 어린이 도서 연구회 추천 책 가져오기
 */
export async function getResearchCouncilBooks(limit: number = 5): Promise<Book[]> {
    const supabase = createClient()

    const { data, error } = await supabase
        .from('childbook_items')
        .select('id, title, author, publisher, category, age, pangyo_callno, image_url, curation_tag')
        .eq('curation_tag', '어린이도서연구회')
        .or('is_hidden.is.null,is_hidden.eq.false')
        .limit(limit)

    if (error) {
        console.error('Error fetching research council books:', error)
        return []
    }

    return data || []
}
