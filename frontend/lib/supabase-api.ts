import { SupabaseClient } from '@supabase/supabase-js'
import { Book, RatedBook } from './types'

const QA_MOCK_USER_ID = "00000000-0000-0000-0000-000000000000"
const QA_MOCK_STORAGE_KEY = "qa_mock_wishlist_ids"

function getQaMockWishlistIds(): number[] {
    if (typeof window === 'undefined') return []
    try {
        const raw = localStorage.getItem(QA_MOCK_STORAGE_KEY)
        if (!raw) return []
        const parsed = JSON.parse(raw)
        return Array.isArray(parsed) ? parsed.map(Number).filter((n) => !isNaN(n)) : []
    } catch {
        return []
    }
}

function setQaMockWishlistIds(ids: number[]) {
    if (typeof window === 'undefined') return
    try {
        localStorage.setItem(QA_MOCK_STORAGE_KEY, JSON.stringify(ids))
    } catch {
        // ignore
    }
}

export async function saveBook(supabase: SupabaseClient, userId: string, bookId: number) {
    if (userId === QA_MOCK_USER_ID) {
        const ids = getQaMockWishlistIds()
        if (!ids.includes(bookId)) {
            setQaMockWishlistIds([bookId, ...ids])
        }
        return
    }

    // 중복 저장 시 UNIQUE 제약 오류 방지를 위해 upsert 및 ignoreDuplicates 적용
    const { error } = await supabase
        .from('wishlists')
        .upsert([{ user_id: userId, book_id: bookId }], { onConflict: 'user_id,book_id', ignoreDuplicates: true })

    if (error) throw error
}

export async function unsaveBook(supabase: SupabaseClient, userId: string, bookId: number) {
    if (userId === QA_MOCK_USER_ID) {
        const ids = getQaMockWishlistIds()
        setQaMockWishlistIds(ids.filter(id => id !== bookId))
        return
    }

    const { error } = await supabase
        .from('wishlists')
        .delete()
        .match({ user_id: userId, book_id: bookId })

    if (error) throw error
}

export async function getSavedBookIds(supabase: SupabaseClient, userId: string): Promise<number[]> {
    if (userId === QA_MOCK_USER_ID) {
        return getQaMockWishlistIds()
    }

    const { data, error } = await supabase
        .from('wishlists')
        .select('book_id')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })

    if (error) throw error
    return data?.map((item: any) => Number(item.book_id)).filter((id: number) => !isNaN(id)) || []
}

const SAVED_BOOK_SELECT_FIELDS =
    'id, title, author, publisher, isbn, category, age, image_url, curation_tag, national_loan_count, vol, library_info:book_library_info(library_name, callno)'

/**
 * 저장한 책 목록을 wishlists + childbook_items + book_library_info 단일 조인 쿼리로 조회
 * (기존 getSavedBookIds -> FastAPI /api/books/by-ids 2단계 워터폴 제거)
 */
export async function getSavedBooks(supabase: SupabaseClient, userId: string): Promise<Book[]> {
    if (userId === QA_MOCK_USER_ID) {
        const mockIds = getQaMockWishlistIds()
        if (mockIds.length === 0) return []

        const { data: booksData, error: booksError } = await (supabase
            .from('childbook_items')
            .select(SAVED_BOOK_SELECT_FIELDS)
            .in('id', mockIds) as any)

        if (booksError) throw booksError
        const idMap = new Map<number, Book>((booksData || []).map((b: any) => [b.id, b as Book]))
        return mockIds.map((id) => idMap.get(id)).filter((b): b is Book => Boolean(b))
    }

    const { data, error } = await (supabase
        .from('wishlists')
        .select(`book_id, created_at, book:childbook_items(${SAVED_BOOK_SELECT_FIELDS})`)
        .eq('user_id', userId)
        .order('created_at', { ascending: false }) as any)

    if (!error && Array.isArray(data)) {
        return data
            .map((row: any) => (Array.isArray(row.book) ? row.book[0] : row.book))
            .filter((book: any): book is Book => Boolean(book && book.id))
    }

    // Fallback: 조인 실패 시 ID 조회 후 childbook_items 직접 조회
    const savedIds = await getSavedBookIds(supabase, userId)
    if (savedIds.length === 0) return []

    const { data: booksData, error: booksError } = await (supabase
        .from('childbook_items')
        .select(SAVED_BOOK_SELECT_FIELDS)
        .in('id', savedIds) as any)

    if (booksError) throw booksError
    const idMap = new Map<number, Book>((booksData || []).map((b: any) => [b.id, b as Book]))
    return savedIds.map((id) => idMap.get(id)).filter((b): b is Book => Boolean(b))
}

/**
 * 내가 별점/리뷰 남긴 책 목록을 book_reviews + childbook_items 단일 조인 쿼리로 조회
 */
export async function getMyRatedBooksFromSupabase(supabase: SupabaseClient, userId: string): Promise<RatedBook[]> {
    if (userId === "00000000-0000-0000-0000-000000000000") {
        return []
    }

    const { data, error } = await (supabase
        .from('book_reviews')
        .select(`
            id,
            book_id,
            rating,
            created_at,
            book:childbook_items(id, title, author, publisher, isbn, image_url, age, category, curation_tag, description, national_loan_count)
        `)
        .eq('user_id', userId)
        .order('created_at', { ascending: false }) as any)

    if (error) throw error
    if (!Array.isArray(data) || data.length === 0) return []

    const seenBookIds = new Set<number>()
    const ratedBooks: RatedBook[] = []

    for (const r of data) {
        const bid = r.book_id
        if (!bid || seenBookIds.has(bid)) continue
        seenBookIds.add(bid)

        const book = (Array.isArray(r.book) ? r.book[0] : r.book) || {}
        ratedBooks.push({
            review_id: String(r.id || ''),
            id: bid,
            title: book.title || '제목 없음',
            author: book.author ?? null,
            publisher: book.publisher ?? null,
            isbn: book.isbn ?? null,
            image_url: book.image_url ?? null,
            age: book.age ?? null,
            category: book.category ?? null,
            curation_tag: book.curation_tag ?? null,
            description: book.description ?? null,
            national_loan_count: book.national_loan_count ?? null,
            vol: null,
            rating: Number(r.rating ?? 0),
            created_at: String(r.created_at || ''),
        })
    }

    return ratedBooks
}
