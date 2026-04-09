/**
 * 고해상도 이미지 URL로 변환하는 유틸리티
 * .agent/skills/development/image_optimization/SKILL.md 가이드를 따름
 * 
 * @param url 원본 이미지 URL
 * @param size 'list' (200px) 또는 'detail' (500px)
 */
export function getOptimizedImageUrl(url: string | null | undefined, size: 'list' | 'detail' = 'detail'): string {
    if (!url) return '';

    try {
        const urlObj = new URL(url);
        const targetSize = size === 'list' ? 'cover200' : 'cover500';

        // 1. 알라딘 이미지 (image.aladin.co.kr)
        // coversum, cover200 등을 대상 사이즈로 변경
        if (urlObj.hostname.includes('aladin.co.kr')) {
            return url
                .replace('/coversum/', `/${targetSize}/`)
                .replace('/cover200/', `/${targetSize}/`)
                .replace('/cover500/', `/${targetSize}/`)
                .replace(/\/cover\d+\//, `/${targetSize}/`);
        }

        // 2. 네이버 이미지 (pstatic.net)
        // type 파라미터를 제거하여 원본(고해상도) 이미지를 가져옴
        // (네이버는 Next.js Image가 리사이징을 처리하도록 원본 전달)
        if (urlObj.hostname.includes('pstatic.net')) {
            urlObj.searchParams.delete('type');
            return urlObj.toString();
        }

        return url;
    } catch {
        const targetSize = size === 'list' ? 'cover200' : 'cover500';
        if (url.includes('aladin.co.kr')) {
            return url.replace(/\/cover(sum|\d+)\//, `/${targetSize}/`);
        }
        if (url.includes('pstatic.net')) {
            return url.replace(/\?type=[a-zA-Z0-9_]+/, '');
        }
        return url;
    }
}

// 기존 함수와 호환성 유지 (주로 상세 페이지용)
export function getHighResImageUrl(url: string | null | undefined): string {
    return getOptimizedImageUrl(url, 'detail');
}
