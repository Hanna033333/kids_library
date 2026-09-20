/**
 * 큐레이션 필터 유틸리티 (SSOT - Single Source of Truth)
 *
 * URL 파라미터 → DB 태그 매핑, 특수 태그 판별, 기본 정렬 결정 로직을
 * supabase-client.ts / books-api-server.ts 양쪽에서 공유합니다.
 */

/** URL 파라미터 값 → DB curation_tag 값 매핑 */
export const CURATION_TAG_MAPPING: Record<string, string> = {
  '겨울방학': '겨울방학2026',       // Backward compatibility
  'winter-vacation': '겨울방학2026',
  'summer-vacation': '여름방학2026',
  '어린이도서연구회': '어린이도서연구회', // Backward compatibility
  'research-council': '어린이도서연구회',
  '교과서수록': '교과서수록',
  'textbook': '교과서수록',
}

/** ilike '%tag%' 매칭을 사용하는 특수 큐레이션 태그 목록 */
export const SPECIAL_CURATION_TAGS = ['겨울방학2026', '여름방학2026', '어린이도서연구회', 'caldecott', '교과서수록'] as const

/** 특별 큐레이션으로 분류되는 URL 파라미터 값 목록 (정렬 기본값 결정 시 사용) */
export const SPECIAL_CURATION_PARAMS = [
  'caldecott', 'winter-vacation', '겨울방학', 'summer-vacation', '여름방학', '여름방학2026', 'research-council', '어린이도서연구회', 'textbook', '교과서수록'
] as const

/**
 * URL 파라미터 값을 DB curation_tag 값으로 변환합니다.
 */
export function resolveDbCurationTag(urlParam: string): string {
  return CURATION_TAG_MAPPING[urlParam] || urlParam
}

/**
 * 해당 DB 태그가 특수(Special) 큐레이션인지 판별합니다.
 * Special 태그는 ilike '%tag%' 매칭을 사용합니다.
 */
export function isSpecialTag(dbTag: string): boolean {
  return (SPECIAL_CURATION_TAGS as readonly string[]).includes(dbTag)
}

/**
 * 큐레이션 + 연령 필터 상태에 따른 기본 정렬 필드를 결정합니다.
 * 특별 큐레이션 또는 연령대 필터가 적용된 경우 제목(ㄱㄴㄷ 순)으로 기본 정렬합니다.
 */
export function resolveDefaultSortField(
  currentSort: string | undefined,
  curation: string | undefined,
  age: string | undefined,
): string {
  const sortField = currentSort || 'pangyo_callno'

  const isSpecialCuration = !!curation &&
    (SPECIAL_CURATION_PARAMS as readonly string[]).includes(curation)

  if ((sortField === 'pangyo_callno' || !currentSort) && (isSpecialCuration || age)) {
    return 'title'
  }

  return sortField
}

/**
 * 일반(비특수) 큐레이션 태그에 대한 첫 번째 태그 정밀 매칭 OR 필터 문자열을 생성합니다.
 */
export function buildCurationOrFilter(dbTag: string): string {
  return `curation_tag.eq."${dbTag}",curation_tag.like."${dbTag},%",curation_tag.eq."#${dbTag}",curation_tag.like."#${dbTag},%"`
}

/**
 * 여름방학 추천도서 큐레이션 활성화 여부 확인 (8/20까지만 활성화)
 * KST 기준 2026년 8월 20일 23:59:59 (YYYY-MM-DD <= '2026-08-20') 까지만 true 반환
 */
export function isSummerCurationActive(targetDate: Date = new Date()): boolean {
  const utc = targetDate.getTime() + (targetDate.getTimezoneOffset() * 60 * 1000)
  const kst = new Date(utc + (9 * 60 * 60 * 1000))
  const yyyy = kst.getFullYear()
  const mm = String(kst.getMonth() + 1).padStart(2, '0')
  const dd = String(kst.getDate()).padStart(2, '0')
  const dateStr = `${yyyy}-${mm}-${dd}`

  return dateStr <= '2026-08-20'
}

/**
 * 도서 카드/상세에서 UI에 노출하지 않는 특수 태그 목록 (SSOT)
 * BookItem, BookDetailClient 등 모든 UI 컴포넌트가 이 목록을 공유합니다.
 */
export const HIDDEN_UI_TAGS = new Set<string>([])

/**
 * UI 표시용 큐레이션 태그 한글 변환 매핑
 */
export const TAG_DISPLAY_NAMES: Record<string, string> = {
  'caldecott': '칼데콧',
  'research-council': '어린이도서연구회',
  'winter-vacation': '겨울방학',
  'summer-vacation': '여름방학',
  '여름방학2026': '여름방학',
  '겨울방학2026': '겨울방학',
  'textbook': '교과서수록',
  '교과서수록': '교과서수록',
  '초등1학년': '초등 1학년',
  '초등2학년': '초등 2학년',
  '초등3학년': '초등 3학년',
  '초등4학년': '초등 4학년',
  '초등5학년': '초등 5학년',
  '초등6학년': '초등 6학년',
}

/**
 * 큐레이션 태그 문자열을 안전하게 정제합니다 (오염된 쿼리스트링 ? & 제거, # 제거, 공백 제거)
 */
export function cleanCurationTag(tag: string | null | undefined): string {
  if (!tag) return ''
  return tag.replace(/^#/, '').split(/[?&]/)[0].trim()
}

/**
 * 큐레이션 태그를 UI 표시용 명칭(한글)으로 변환합니다.
 * @example formatCurationTag('caldecott') → '칼데콧'
 */
export function formatCurationTag(tag: string | null | undefined): string {
  if (!tag) return ''
  const clean = cleanCurationTag(tag)
  return TAG_DISPLAY_NAMES[clean] || clean
}

/**
 * 해당 태그가 초등 학년 태그(예: '초등1학년', '1학년', '#초등2학년')인지 판별합니다.
 */
export function isGradeTag(tag: string | null | undefined): boolean {
  if (!tag) return false
  const clean = cleanCurationTag(tag)
  return /^초등\s*[1-6]학년$/.test(clean) || /^[1-6]학년$/.test(clean)
}

/**
 * book.curation_tag 문자열을 파싱하여 UI에 표시할 태그 배열을 반환합니다. (SSOT)
 *
 * - `#` 접두사 제거 및 오염된 쿼리스트링(? &) 분리 정제
 * - HIDDEN_UI_TAGS에 속하는 특수 태그 제외
 * - limit 개수만큼만 반환 (기본 전체)
 *
 * @example
 * parseCurationTags('잠자리, caldecott, 가족사랑', 2) → ['잠자리', '가족사랑']
 */
export function parseCurationTags(raw: string | null | undefined, limit?: number): string[] {
  if (!raw) return []
  const tags = raw
    .split(/[,/]/)
    .map((t) => cleanCurationTag(t))
    .filter((t) => t && !HIDDEN_UI_TAGS.has(t))
  const uniqueTags = Array.from(new Set(tags))
  return limit !== undefined ? uniqueTags.slice(0, limit) : uniqueTags
}

/**
 * curation_tag 문자열에서 첫 번째 학년 태그를 추출합니다.
 */
export function extractGradeTag(raw: string | null | undefined): string | null {
  if (!raw) return null
  const tags = parseCurationTags(raw)
  const gradeTag = tags.find((t) => isGradeTag(t))
  return gradeTag ?? null
}

/**
 * book.curation_tag의 첫 번째 유효 태그를 반환합니다.
 * 큐레이션 목록 링크 등 단일 태그가 필요한 곳에서 사용합니다.
 *
 * @example
 * getFirstCurationTag('caldecott, 가족사랑') → '가족사랑'
 */
export function getFirstCurationTag(raw: string | null | undefined): string {
  return parseCurationTags(raw, 1)[0] ?? ''
}

/**
 * book.curation_tag에서 특수 태그(교과서수록, 방학, 칼데콧 등) 및 학년 태그를 제외한
 * 순수 AI 주제/내용 큐레이션 태그 중 첫 번째 태그를 반환합니다.
 *
 * @example
 * getTopicCurationTag('교과서수록, 초등1학년, 친구관계, 상상력') → '친구관계'
 * getTopicCurationTag('가족사랑, 감정표현') → '가족사랑'
 */
export function getTopicCurationTag(raw: string | null | undefined): string {
  if (!raw) return ''
  const tags = parseCurationTags(raw)
  const topicTag = tags.find((t) => !isSpecialTag(t) && !isGradeTag(t))
  return topicTag ?? ''
}

/**
 * 도서 상세의 1번 대표 큐레이션 태그를 결정합니다.
 * 교과서수록, 칼데콧, 방학 등 특수 큐레이션 태그가 포함되어 있다면 특수 태그를 우선 반환하고,
 * 일반 도서인 경우 첫 번째 태그를 반환합니다.
 *
 * @example
 * getPrimaryCurationTag('상상력, 교과서수록, 초등1학년') → '교과서수록'
 * getPrimaryCurationTag('가족사랑, 감정표현') → '가족사랑'
 */
export function getPrimaryCurationTag(raw: string | null | undefined): string {
  if (!raw) return ''
  const tags = parseCurationTags(raw)
  const specialTag = tags.find((t) => isSpecialTag(t))
  if (specialTag) return specialTag
  return tags[0] ?? ''
}

