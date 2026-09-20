/**
 * 큐레이션 "더보기" 링크 생성 유틸리티 (SSOT)
 *
 * 홈 화면, 도서 상세, 검색 결과 등 어디서든 더보기 링크를 조립할 때
 * 이 함수 하나만 호출하면 됩니다. 파라미터 누락으로 목록 진입 시
 * 순서가 달라지는 문제를 원천 차단합니다.
 */

import { findCurationByTag } from '@/lib/constants/curation-categories'
import { SPECIAL_CURATION_PARAMS, cleanCurationTag } from '@/lib/utils/curation-filter'

export interface CurationMoreLinkOptions {
  /** 큐레이션 태그 (예: '자연관찰', '교과서수록', 'caldecott') */
  curation?: string | null
  /** 연령 그룹 키 (예: '8-12', '4-7') */
  age?: string | null
  /** 학년 태그 (예: '초등5학년') */
  tag?: string | null
  /** 정렬 기준 (예: 'popular', 'confidence_score_desc') */
  sort?: string | null
}

/**
 * 큐레이션 섹션의 "더보기" 링크를 조립합니다.
 *
 * 규칙:
 * 1. 특수 큐레이션(칼데콧, 방학, 연구회 등)은 age/tag를 넘기지 않음 (전체 목록)
 * 2. 교과서수록은 항상 /books?curation=교과서수록 (학년 tag만 선택적)
 * 3. AI 주제 큐레이션은 slug가 있으면 /collections/curation/[slug], 없으면 /books?curation=...
 * 4. 큐레이션 없이 age만 있으면 /books?age=...
 * 5. 모든 유효한 파라미터(age, tag, sort)를 쿼리스트링에 자동 포함
 */
export function getCurationMoreLink(options: CurationMoreLinkOptions): string {
  let { curation, age, tag, sort } = options

  // curation 파라미터 오염 방어: ? 또는 & 로 붙어 들어온 쿼리스트링 자동 분리
  if (curation && (curation.includes('?') || curation.includes('&'))) {
    try {
      const parts = curation.split(/[?&]/)
      const pureTag = parts[0]
      const queryString = curation.substring(pureTag.length + 1)
      const urlParams = new URLSearchParams(queryString)
      if (!age && urlParams.get('age')) age = urlParams.get('age')
      if (!tag && urlParams.get('tag')) tag = urlParams.get('tag')
      if (!sort && urlParams.get('sort')) sort = urlParams.get('sort')
      curation = pureTag
    } catch {
      curation = cleanCurationTag(curation)
    }
  } else if (curation) {
    curation = cleanCurationTag(curation)
  }

  // 큐레이션이 없으면 연령별 목록 링크
  if (!curation) {
    const params = new URLSearchParams()
    if (age) params.set('age', age)
    if (sort) params.set('sort', sort)
    const qStr = params.toString()
    return `/books${qStr ? `?${qStr}` : ''}`
  }

  // 특수 큐레이션인지 판별
  const isSpecial = (SPECIAL_CURATION_PARAMS as readonly string[]).includes(curation)

  // 교과서수록: /books?curation=교과서수록[&tag=...]
  if (curation === '교과서수록' || curation === 'textbook') {
    const params = new URLSearchParams()
    params.set('curation', '교과서수록')
    if (tag) params.set('tag', tag)
    return `/books?${params.toString()}`
  }

  // 특수 큐레이션(칼데콧, 방학, 연구회 등): age/tag 미포함
  if (isSpecial) {
    return `/books?curation=${encodeURIComponent(curation)}`
  }

  // AI 주제 큐레이션: slug가 있으면 /collections/curation/[slug]
  const matched = findCurationByTag(curation)
  if (matched) {
    const params = new URLSearchParams()
    if (age) params.set('age', age)
    if (tag) params.set('tag', tag)
    if (sort) params.set('sort', sort)
    const qStr = params.toString()
    return `/collections/curation/${encodeURIComponent(matched.slug)}${qStr ? `?${qStr}` : ''}`
  }

  // 매칭되지 않는 일반/서브 태그 큐레이션: /books?curation=...
  const params = new URLSearchParams()
  params.set('curation', curation)
  if (age) params.set('age', age)
  if (tag) params.set('tag', tag)
  if (sort) params.set('sort', sort)
  return `/books?${params.toString()}`
}
