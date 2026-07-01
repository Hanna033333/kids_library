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

