/**
 * DB의 age 값(예: '5세부터')을 서비스 공통 연령대 라벨(예: '4~7세')로 변환합니다.
 */
export function getAgeDisplayLabel(dbAge: string | null): string {
    if (!dbAge) return '';

    // 정확한 매칭 우선 적용
    if (
        dbAge === '0세부터' ||
        dbAge === '1세부터' ||
        dbAge === '2세부터' ||
        dbAge === '3세부터' ||
        dbAge === '0-3'
    ) {
        return '0~3세';
    }

    if (
        dbAge === '4세부터' ||
        dbAge === '5세부터' ||
        dbAge === '6세부터' ||
        dbAge === '7세부터' ||
        dbAge === '4-7' ||
        dbAge.includes('유아')
    ) {
        return '4~7세';
    }

    if (
        dbAge === '8세부터' ||
        dbAge === '9세부터' ||
        dbAge === '10세부터' ||
        dbAge === '11세부터' ||
        dbAge === '12세부터' ||
        dbAge === '8-12'
    ) {
        return '8~12세';
    }

    if (
        dbAge === '13세부터' ||
        dbAge === '16세부터' ||
        dbAge === '13+' ||
        dbAge === 'teen'
    ) {
        return '13세 이상';
    }

    // fallback: 숫자를 안전하게 정규식으로 파싱하여 처리
    const match = dbAge.match(/(\d+)세/);
    if (match) {
        const ageNum = parseInt(match[1], 10);
        if (ageNum >= 0 && ageNum <= 3) return '0~3세';
        if (ageNum >= 4 && ageNum <= 7) return '4~7세';
        if (ageNum >= 8 && ageNum <= 12) return '8~12세';
        if (ageNum >= 13) return '13세 이상';
    }

    // 매핑되지 않은 경우 원래 값 반환
    return dbAge;
}

/**
 * DB의 age 값(예: '5세부터')을 AGE_MAP의 키(예: '4-7')로 역변환합니다.
 */
export function getAgeGroupKey(dbAge: string | null): string {
    if (!dbAge) return '0-3';

    if (
        dbAge === '0세부터' ||
        dbAge === '1세부터' ||
        dbAge === '2세부터' ||
        dbAge === '3세부터' ||
        dbAge === '0-3'
    ) {
        return '0-3';
    }

    if (
        dbAge === '4세부터' ||
        dbAge === '5세부터' ||
        dbAge === '6세부터' ||
        dbAge === '7세부터' ||
        dbAge === '4-7' ||
        dbAge.includes('유아')
    ) {
        return '4-7';
    }

    if (
        dbAge === '8세부터' ||
        dbAge === '9세부터' ||
        dbAge === '10세부터' ||
        dbAge === '11세부터' ||
        dbAge === '12세부터' ||
        dbAge === '8-12'
    ) {
        return '8-12';
    }

    if (
        dbAge === '13세부터' ||
        dbAge === '16세부터' ||
        dbAge === '13+' ||
        dbAge === 'teen'
    ) {
        return '13+';
    }

    const match = dbAge.match(/(\d+)세/);
    if (match) {
        const ageNum = parseInt(match[1], 10);
        if (ageNum >= 0 && ageNum <= 3) return '0-3';
        if (ageNum >= 4 && ageNum <= 7) return '4-7';
        if (ageNum >= 8 && ageNum <= 12) return '8-12';
        if (ageNum >= 13) return '13+';
    }

    return '0-3'; // fallback
}

/**
 * 주어진 연령 키('0-3', '4-7', '8-12', '13+')와 도서의 연령이 일치하는지 판별합니다.
 */
export function isBookMatchingAge(book: { age?: string | null; curation_tag?: string | null }, targetAgeKey: string): boolean {
    if (!targetAgeKey) return false;

    // 1. 도서 age 컬럼 매칭
    if (book.age) {
        const bookAgeKey = getAgeGroupKey(book.age);
        if (bookAgeKey === targetAgeKey) return true;
    }

    // 2. curation_tag에 연령 태그 포함 여부 (#0~3세, #4~7세, #8~12세, #13세 이상 등)
    if (book.curation_tag) {
        const displayLabel = getAgeDisplayLabel(targetAgeKey);
        if (displayLabel && book.curation_tag.includes(displayLabel)) return true;
        if (book.curation_tag.includes(targetAgeKey)) return true;

        // 초등 학년 태그 매칭 (8~12세인 경우 초등 1~6학년 매칭)
        if (targetAgeKey === '8-12' && /초등\s*[1-6]학년/.test(book.curation_tag)) {
            return true;
        }
    }

    return false;
}

/**
 * 도서 리스트에서 사용자의 선호 연령대에 맞는 도서를 맨 앞으로 우선 배치합니다.
 * @param books 원본 도서 목록
 * @param preferredAge 선호 연령 키 ('0-3' | '4-7' | '8-12' | '13+')
 * @param limit 반환할 최대 권수 (기본값: 원본 길이 또는 7)
 */
export function sortBooksByAgePreference<T extends { age?: string | null; curation_tag?: string | null }>(
    books: T[],
    preferredAge: string | null | undefined,
    limit?: number
): T[] {
    if (!books || books.length === 0) return [];
    if (!preferredAge || !['0-3', '4-7', '8-12', '13+'].includes(preferredAge)) {
        return typeof limit === 'number' ? books.slice(0, limit) : books;
    }

    const matched: T[] = [];
    const others: T[] = [];

    for (const book of books) {
        if (isBookMatchingAge(book, preferredAge)) {
            matched.push(book);
        } else {
            others.push(book);
        }
    }

    const combined = [...matched, ...others];
    return typeof limit === 'number' ? combined.slice(0, limit) : combined;
}

