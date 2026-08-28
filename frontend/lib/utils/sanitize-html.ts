/**
 * 외부(알라딘 등) API가 내려주는 도서 소개 HTML을 dangerouslySetInnerHTML에 넣기 전
 * 최소한의 화이트리스트 방식으로 정제합니다.
 *
 * 별도 sanitizer 라이브러리(dompurify 등)를 새로 추가하는 대신 순수 정규식 기반으로
 * 구현했습니다 — 완전한 HTML 파서는 아니지만, <script>/<iframe>/이벤트 핸들러 속성/
 * javascript: 스킴처럼 실제 실행 가능한 벡터를 걷어내는 데 목적을 둡니다.
 * 신뢰할 수 없는 임의의 HTML을 다뤄야 하는 다른 용도로는 사용하지 마세요.
 */

const ALLOWED_TAGS = new Set([
    'b', 'strong', 'i', 'em', 'u', 'br', 'p', 'span', 'div',
    'ul', 'ol', 'li', 'blockquote', 'sup', 'sub',
])

// 위험한 태그는 내용까지 통째로 제거 (여는 태그만 지우면 내부 스크립트가 텍스트로 노출됨)
const STRIP_WITH_CONTENT = /<(script|style|iframe|object|embed|link|meta|form|svg)[^>]*>[\s\S]*?<\/\1\s*>/gi
const STRIP_SELF_CLOSING_DANGEROUS = /<(script|style|iframe|object|embed|link|meta|form|svg)[^>]*\/?>/gi

export function sanitizeDescriptionHtml(raw: string | null | undefined): string {
    if (!raw) return ''

    let html = raw
        .replace(STRIP_WITH_CONTENT, '')
        .replace(STRIP_SELF_CLOSING_DANGEROUS, '')

    // 남은 모든 태그의 속성을 제거하고, 화이트리스트에 없는 태그는 통째로 걷어낸다.
    html = html.replace(/<\/?([a-zA-Z0-9]+)([^>]*)>/g, (match, rawTag) => {
        const tag = String(rawTag).toLowerCase()
        const isClosing = match.startsWith('</')

        if (!ALLOWED_TAGS.has(tag)) {
            return ''
        }

        return isClosing ? `</${tag}>` : `<${tag}>`
    })

    return html
}
