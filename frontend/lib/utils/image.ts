/**
 * 고해상도 이미지 URL로 변환하는 유틸리티
 * .agent/skills/development/image_optimization/SKILL.md 가이드를 따름
 */
export function getHighResImageUrl(url: string | null | undefined): string {
    if (!url) return '';

    try {
        const urlObj = new URL(url);

        // 1. 알라딘 이미지 (image.aladin.co.kr)
        // coversum, cover200 등을 cover500으로 변경
        if (urlObj.hostname.includes('aladin.co.kr')) {
            return url
                .replace('/coversum/', '/cover500/')
                .replace('/cover200/', '/cover500/')
                // 만약 다른 숫자가 들어있을 경우를 대비한 정규식 (옵션)
                .replace(/\/cover\d+\//, '/cover500/');
        }

        // 2. 네이버 이미지 (pstatic.net)
        // type 파라미터를 제거하여 원본(고해상도) 이미지를 가져옴
        if (urlObj.hostname.includes('pstatic.net')) {
            urlObj.searchParams.delete('type');
            return urlObj.toString();
        }

        // 3. 기타 (YES24, 교보 등) - 필요 시 확장
        return url;
    } catch {
        // 유효하지 않은 URL이거나 상대 경로인 경우 기본 처리
        if (url.includes('aladin.co.kr')) {
            return url.replace(/\/cover(sum|\d+)\//, '/cover500/');
        }
        if (url.includes('pstatic.net')) {
            return url.replace(/\?type=[a-zA-Z0-9_]+/, '');
        }
        return url;
    }
}
