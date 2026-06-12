/**
 * 연령 그룹 단일 진실 공급원 (SSOT - Single Source of Truth)
 *
 * 프론트엔드 연령 키(ageGroup) → Supabase DB 연령 값 매핑.
 * home-api.ts, supabase-client.ts 양쪽에서 동일하게 사용합니다.
 */

export const AGE_MAP: Record<string, string[]> = {
  '0-3': ['0세부터', '3세부터'],
  '4-7': ['5세부터', '7세부터', '유아'],
  '8-12': ['9세부터', '11세부터'],
  'teen': ['13세부터', '16세부터'],
  '13+': ['13세부터', '16세부터'],
} as const
