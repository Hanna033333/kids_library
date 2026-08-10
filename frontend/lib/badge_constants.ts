/**
 * 범용 10종 부모 공감 뱃지 상수 정의
 * 네이버 플레이스 스타일의 위트있는 평가 뱃지 시스템
 */

export interface Badge {
  emoji: string;
  label: string;
  full: string; // emoji + label (API 전송용)
}

export const BADGES: Badge[] = [
  { emoji: '🎨', label: '그림체가 좋아요', full: '🎨 그림체가 좋아요' },
  { emoji: '😆', label: '깔깔 웃으며 무한 반복 요청해요', full: '😆 깔깔 웃으며 무한 반복 요청해요' },
  { emoji: '📖', label: '글밥이 적당해요', full: '📖 글밥이 적당해요' },
  { emoji: '🧠', label: '호기심이 부쩍 늘었어요', full: '🧠 호기심이 부쩍 늘었어요' },
  { emoji: '⭐', label: '매일 밤 가져오는 최애 책이에요', full: '⭐ 매일 밤 가져오는 최애 책이에요' },
  { emoji: '💬', label: '아이와 대화거리가 풍부해져요', full: '💬 아이와 대화거리가 풍부해져요' },
  { emoji: '💡', label: '새로운 상상력을 자극해요', full: '💡 새로운 상상력을 자극해요' },
  { emoji: '📚', label: '도서관에서 꼭 빌려볼 만해요', full: '📚 도서관에서 꼭 빌려볼 만해요' },
  { emoji: '☀️', label: '아이 혼자서도 잘 펼쳐봐요', full: '☀️ 아이 혼자서도 잘 펼쳐봐요' },
  { emoji: '👏', label: '아이 집중력이 엄청 높아져요', full: '👏 아이 집중력이 엄청 높아져요' },
];

/** 뱃지 full 텍스트로 Badge 객체 찾기 */
export function findBadge(full: string): Badge | undefined {
  return BADGES.find((b) => b.full === full);
}
