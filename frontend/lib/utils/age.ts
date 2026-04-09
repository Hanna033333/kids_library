/**
 * DB의 age 값(예: '5세부터')을 서비스 공통 연령대 라벨(예: '4~7세')로 변환합니다.
 */
export function getAgeDisplayLabel(dbAge: string | null): string {
    if (!dbAge) return '';

    // 0~3세: '0세부터', '1세부터', '2세부터', '3세부터', '0-3'
    if (
        dbAge.includes('0세') ||
        dbAge.includes('1세') ||
        dbAge.includes('2세') ||
        dbAge.includes('3세') ||
        dbAge === '0-3'
    ) {
        return '0~3세';
    }

    // 4~7세: '5세부터', '7세부터', '4-7'
    if (
        dbAge.includes('5세') ||
        dbAge.includes('7세') ||
        dbAge === '4-7' ||
        dbAge.includes('유아')
    ) {
        return '4~7세';
    }

    // 8~12세: '9세부터', '11세부터', '8-12'
    if (
        dbAge.includes('8세') ||
        dbAge.includes('9세') ||
        dbAge.includes('11세') ||
        dbAge === '8-12'
    ) {
        return '8~12세';
    }

    // 13세 이상: '13세부터', '16세부터', '13+', 'teen'
    if (
        dbAge.includes('13') ||
        dbAge.includes('16') ||
        dbAge === '13+' ||
        dbAge === 'teen'
    ) {
        return '13세 이상';
    }

    // 매핑되지 않은 경우 원래 값 반환
    return dbAge;
}
