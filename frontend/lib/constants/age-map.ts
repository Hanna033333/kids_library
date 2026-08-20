/**
 * 연령 그룹 표준 키 목록 (SSOT - Single Source of Truth)
 *
 * DB age 컬럼은 프론트엔드 키와 동일한 값으로 표준화되었습니다.
 * ('0-3', '4-7', '8-12', '13+')
 * AGE_MAP은 하위 호환을 위해 유지되나 1:1 매핑으로 단순화되었습니다.
 */

export const AGE_MAP: Record<string, string[]> = {
  '0-3': ['0-3'],
  '4-7': ['4-7'],
  '8-12': ['8-12'],
  '13+': ['13+'],
  'teen': ['13+'], // 하위 호환
} as const

/** 연령 그룹 표준 키 */
export const AGE_GROUPS = ['0-3', '4-7', '8-12', '13+'] as const
export type AgeGroup = typeof AGE_GROUPS[number]
