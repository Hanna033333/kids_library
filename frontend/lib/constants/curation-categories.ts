import { ALL_TAXONOMY, CurationTag } from './taxonomy';

export interface CurationCategory {
  id: string;
  name: string;
  icon?: string;
}

export const CURATION_CATEGORIES: CurationCategory[] = [
  { id: 'all', name: '전체' },
  { id: 'emotion', name: '💖 마음·정서' },
  { id: 'social', name: '🤝 사회성·생활' },
  { id: 'nature_science', name: '🔬 호기심·자연' },
  { id: 'art_imagination', name: '🎨 예술·상상' },
  { id: 'special', name: '🏆 특별 기획' },
];

export interface UnifiedCurationItem {
  id: number | string;
  subtitle: string;
  title: string;
  tag: string;
  slug: string;
  category: 'emotion' | 'social' | 'nature_science' | 'art_imagination' | 'special';
}

// ALL_TAXONOMY에 없는 외부 정적 특수 큐레이션 (칼데콧, 어린이도서연구회)
const NON_TAXONOMY_SPECIALS: UnifiedCurationItem[] = [
  {
    id: 'special-caldecott',
    subtitle: '세계 최고 권위의 그림책 노벨상',
    title: '🏆 칼데콧 수상작',
    tag: '칼데콧',
    slug: 'caldecott',
    category: 'special',
  },
  {
    id: 'special-research',
    subtitle: '엄마표 독서 고민 끝! 전문가 엄선',
    title: '📚 어린이도서연구회 추천',
    tag: '어린이도서연구회',
    slug: 'research-council',
    category: 'special',
  },
];

// ALL_TAXONOMY 중 특별 기획으로 분류할 slug 목록
const SPECIAL_TAXONOMY_SLUGS = ['summer-vacation', 'textbook'];

export const SPECIAL_CURATIONS: UnifiedCurationItem[] = [
  ...NON_TAXONOMY_SPECIALS,
  ...ALL_TAXONOMY.filter(item => SPECIAL_TAXONOMY_SLUGS.includes(item.slug)).map((item): UnifiedCurationItem => ({
    id: `special-${item.slug}`,
    subtitle: item.subtitle,
    title: item.title,
    tag: item.tag,
    slug: item.slug,
    category: 'special',
  })),
];

// 태그별 카테고리 매핑 규칙
const CATEGORY_MAP: Record<string, 'emotion' | 'social' | 'nature_science' | 'art_imagination'> = {
  // 💖 마음·정서
  '잠자리': 'emotion',
  '자존감': 'emotion',
  '배려': 'emotion',
  '생명존중': 'emotion',
  '가족사랑': 'emotion',
  '상실': 'emotion',
  '용기': 'emotion',
  '위로': 'emotion',
  '행복': 'emotion',
  '용서': 'emotion',
  '분노조절': 'emotion',
  '감정조절': 'emotion',
  '질투': 'emotion',
  '두려움': 'emotion',
  '슬픔': 'emotion',
  '끈기': 'emotion',

  // 🤝 사회성·생활
  '적응': 'social',
  '우정': 'social',
  '정직': 'social',
  '나눔': 'social',
  '사회성': 'social',
  '규칙': 'social',
  '다문화': 'social',
  '다양성': 'social',
  '진로': 'social',
  '경제': 'social',
  '평화': 'social',
  '장애': 'social',
  '이웃': 'social',
  '미디어': 'social',
  '생활습관': 'social',
  '신체활동': 'social',
  '의사소통': 'social',
  '양성평등': 'social',

  // 🔬 호기심·자연
  '인체': 'nature_science',
  '자연관찰': 'nature_science',
  '환경보호': 'nature_science',
  '과학원리': 'nature_science',
  '곤충': 'nature_science',
  '우주': 'nature_science',
  '공룡': 'nature_science',
  '바다': 'nature_science',
  '날씨': 'nature_science',
  '인공지능': 'nature_science',
  '수학': 'nature_science',
  '발명': 'nature_science',
  '인문지리': 'nature_science',
  '동물도감': 'nature_science',
  '동물': 'nature_science',
  '식물': 'nature_science',
  '코딩': 'nature_science',
  '계절': 'nature_science',
  '자연재해': 'nature_science',

  // 🎨 예술·상상
  '우리문화': 'art_imagination',
  '역사이야기': 'art_imagination',
  '전래동화': 'art_imagination',
  '예술감성': 'art_imagination',
  '연극': 'art_imagination',
  '세계역사': 'art_imagination',
  '명화': 'art_imagination',
  '건축': 'art_imagination',
  '명절': 'art_imagination',
  '한글': 'art_imagination',
  '글쓰기': 'art_imagination',
  '모험': 'art_imagination',
  '판타지': 'art_imagination',
  '유머': 'art_imagination',
  '추리': 'art_imagination',
  '상상력': 'art_imagination',
  '하늘': 'art_imagination',
  '요리': 'art_imagination',
  '패션': 'art_imagination',
  '탈것': 'art_imagination',
  '스포츠': 'art_imagination',
  '미래상상': 'art_imagination',
  '미래도시': 'art_imagination',
  '음악': 'art_imagination',
  '전통놀이': 'art_imagination',
  '괴물': 'art_imagination',
};

export const UNIFIED_TAXONOMY: UnifiedCurationItem[] = [
  ...SPECIAL_CURATIONS,
  ...ALL_TAXONOMY.filter(item => !SPECIAL_TAXONOMY_SLUGS.includes(item.slug)).map((item): UnifiedCurationItem => ({
    id: item.id,
    subtitle: item.subtitle,
    title: item.title,
    tag: item.tag,
    slug: item.slug,
    category: CATEGORY_MAP[item.tag] || 'art_imagination',
  })),
];

export interface SituationPrescription {
  id: string;
  icon: string;
  name: string;
  title: string;
  description: string;
  tags: string[];
}

export const SITUATION_PRESCRIPTIONS: SituationPrescription[] = [
  {
    id: 'all',
    icon: '✨',
    name: '전체 테마',
    title: '50여 가지 맞춤 큐레이션 서가',
    description: '아이의 연령과 정서, 관심사에 딱 맞는 모든 도서 큐레이션을 둘러보세요.',
    tags: [],
  },
  {
    id: 'habit_sleep',
    icon: '💤',
    name: '잠자리·생활습관',
    title: '잠투정 없이 꿀잠 & 바른 생활습관',
    description: '수면 독립과 스스로 씻고 정리하는 올바른 생활 태도를 길러줘요.',
    tags: ['잠자리', '생활습관', '미디어', '신체활동', '경제', '요리', '패션'],
  },
  {
    id: 'emotion_mind',
    icon: '💖',
    name: '마음·감정조절',
    title: '벅찬 감정을 다독이고 자존감 높이기',
    description: '화를 가라앉히고 두려움을 이겨내며 스스로를 사랑하는 마음을 키워요.',
    tags: ['자존감', '분노조절', '두려움', '질투', '슬픔', '위로', '용기', '행복', '용서', '끈기'],
  },
  {
    id: 'social_friends',
    icon: '🏫',
    name: '기관적응·친구',
    title: '첫 어린이집·유치원 적응 & 사이좋은 친구',
    description: '새로운 환경이 즐거워지고 양보와 배려, 규칙을 배워요.',
    tags: ['적응', '사회성', '우정', '배려', '나눔', '규칙', '가족사랑', '이웃', '다문화', '장애', '평화', '진로', '의사소통', '양성평등'],
  },
  {
    id: 'curiosity_explore',
    icon: '🦖',
    name: '호기심·첫지식',
    title: '공룡부터 우주까지, 신나는 탐구 여행',
    description: '아이가 좋아하는 관심사로 책 읽는 즐거움과 세상의 원리를 깨워요.',
    tags: ['공룡', '우주', '자연관찰', '바다', '인체', '과학원리', '곤충', '탈것', '날씨', '동물도감', '동물', '수학', '발명', '코딩', '인공지능', '식물', '환경보호', '인문지리'],
  },
  {
    id: 'art_imagination',
    icon: '🎨',
    name: '상상·예술·역사',
    title: '풍부한 상상력과 우리 문화·이야기',
    description: '옛이야기와 명화, 신비한 모험 속에서 감성과 창의력을 넓혀요.',
    tags: ['상상력', '모험', '판타지', '유머', '전래동화', '우리문화', '역사이야기', '명화', '예술감성', '한글', '글쓰기', '추리', '명절', '연극', '건축', '음악', '세계역사', '전통놀이', '하늘', '괴물', '미래상상', '미래도시'],
  },
  {
    id: 'hall_of_fame',
    icon: '🏆',
    name: '공인 명작',
    title: '전문가와 교과서가 인정한 필독서',
    description: '세계적인 수상작과 교육 전문가, 초등 국어 교과서 수록도서 모음입니다.',
    tags: ['칼데콧', '어린이도서연구회', '교과서수록', '여름방학2026'],
  },
];

/**
 * DB에 저장된 다양한 세부 주제 태그를 공식 큐레이션(UNIFIED_TAXONOMY) 태그로 매핑하는 동의어 사전
 */
export const TAG_SYNONYMS: Record<string, string> = {
  // 학교/기관 적응
  '학교생활': '적응',
  '유치원': '적응',
  '어린이집': '적응',
  '기관적응': '적응',
  // 친구/우정
  '친구관계': '우정',
  '친구': '우정',
  // 감정/마음
  '감정조절': '분노조절',
  '감정표현': '분노조절',
  '감정': '분노조절',
  '마음다스리기': '분노조절',
  '자신감': '자존감',
  '성장': '자존감',
  // 언어/말놀이
  '바른언어': '한글',
  '말놀이': '한글',
  '우리말': '한글',
  '언어': '한글',
  // 이야기/역사
  '옛이야기': '전래동화',
  '역사': '역사이야기',
  '지혜와생각': '과학원리',
  '지혜': '전래동화',
  // 이별/상실
  '이별': '상실',
  // 협력/인성
  '협력': '배려',
  '인성': '정직',
  // 동물/식물
  '동물도감': '생명존중',
  '동물': '생명존중',
};

/**
 * 태그명으로 해당하는 큐레이션 항목(slug 포함)을 찾는 헬퍼 함수
 * (동의어 변환 및 완전 일치 매칭을 최우선으로 하여 오매칭 방지)
 */
export function findCurationByTag(rawTag: string): UnifiedCurationItem | undefined {
  const cleanTag = rawTag.replace(/^#/, '').split(/[?&]/)[0].trim();
  if (!cleanTag) return undefined;

  const normalizedTag = TAG_SYNONYMS[cleanTag] || cleanTag;

  // 1. tag 또는 slug 완전 일치 검사 (동의어 정규화 태그 우선)
  const exactMatch = UNIFIED_TAXONOMY.find(
    item => item.tag === normalizedTag || item.slug === normalizedTag || item.tag === cleanTag || item.slug === cleanTag
  );
  if (exactMatch) return exactMatch;

  // 2. 일치하지 않는 경우 태그 접두/접미 매칭 (예: '초등1학년' -> '교과서수록')
  return UNIFIED_TAXONOMY.find(
    item => item.tag === normalizedTag || normalizedTag.startsWith(item.tag) || cleanTag.startsWith(item.tag)
  );
}

