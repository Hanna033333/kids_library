/**
 * 범용 10종 부모 공감 뱃지 상수 정의
 * 서로 중복되지 않는 독립적 5대 층위 키워드 체계
 */

export interface Badge {
  emoji: string;
  label: string;
  full: string; // emoji + label (API 전송용)
  category: '도서 특징' | '아이 반응';
}

export const BADGE_CATEGORIES = ['도서 특징', '아이 반응'] as const;

export const BADGES: Badge[] = [
  // 1. 도서 특징 (책의 5대 요소: 일러스트/분량/어휘문장/지식생활/메시지)
  { emoji: '🎨', label: '그림체가 예뻐요', full: '🎨 그림체가 예뻐요', category: '도서 특징' },
  { emoji: '📖', label: '글밥이 적당해요', full: '📖 글밥이 적당해요', category: '도서 특징' },
  { emoji: '💡', label: '문장이 아름다워요', full: '💡 문장이 아름다워요', category: '도서 특징' },
  { emoji: '💬', label: '바른 습관을 도와줘요', full: '💬 바른 습관을 도와줘요', category: '도서 특징' },
  { emoji: '📚', label: '교훈과 위안을 줘요', full: '📚 교훈과 위안을 줘요', category: '도서 특징' },

  // 2. 아이 반응 (아동의 5대 독립 반응: 애정도/즐거움/집중도/독립성/호기심)
  { emoji: '⭐', label: '아이 최애 책이에요', full: '⭐ 아이 최애 책이에요', category: '아이 반응' },
  { emoji: '😆', label: '깔깔 웃고 좋아해요', full: '😆 깔깔 웃고 좋아해요', category: '아이 반응' },
  { emoji: '👏', label: '몰입해서 집중해요', full: '👏 몰입해서 집중해요', category: '아이 반응' },
  { emoji: '☀️', label: '혼자서도 잘 봐요', full: '☀️ 혼자서도 잘 봐요', category: '아이 반응' },
  { emoji: '🧠', label: '질문을 많이 해요', full: '🧠 질문을 많이 해요', category: '아이 반응' },
];

/** 뱃지 full 텍스트로 Badge 객체 찾기 */
export function findBadge(full: string): Badge | undefined {
  const exact = BADGES.find((b) => b.full === full);
  if (exact) return exact;

  // 구버전(이전 텍스트) → 신버전 뱃지 폴백 매핑
  // 도서 특징 계열
  if (full.includes('그림체')) return BADGES[0];      // 그림체가 예뻐요
  if (full.includes('글밥')) return BADGES[1];         // 글밥이 적당해요
  if (full.includes('문장') || full.includes('상상력') || full.includes('창의력') || full.includes('표현')) return BADGES[2]; // 문장이 아름다워요
  if (full.includes('습관') || full.includes('대화거리') || full.includes('지식')) return BADGES[3]; // 바른 습관을 도와줘요
  if (full.includes('교훈') || full.includes('위안') || full.includes('구성') || full.includes('꼭 읽어')) return BADGES[4]; // 교훈과 위안을 줘요

  // 아이 반응 계열
  if (full.includes('최애')) return BADGES[5];         // 아이 최애 책이에요
  if (full.includes('웃으') || full.includes('반복') || full.includes('웃고')) return BADGES[6]; // 깔깔 웃고 좋아해요
  if (full.includes('집중') || full.includes('몰입')) return BADGES[7]; // 몰입해서 집중해요
  if (full.includes('혼자서도') || full.includes('펼쳐')) return BADGES[8]; // 혼자서도 잘 봐요
  if (full.includes('질문') || full.includes('호기심')) return BADGES[9]; // 질문을 많이 해요

  return undefined;
}
