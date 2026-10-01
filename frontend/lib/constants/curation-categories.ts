import { ALL_TAXONOMY, CurationTag } from './taxonomy';

export interface CurationCategory {
  id: string;
  name: string;
  icon?: string;
}

export const CURATION_CATEGORIES: CurationCategory[] = [
  { id: 'all', name: '전체' },
  { id: 'emotion', name: '마음·감정' },
  { id: 'social', name: '친구·사회성' },
  { id: 'nature_science', name: '자연·과학' },
  { id: 'art_imagination', name: '상상·이야기' },
  { id: 'special', name: '추천·수상작' },
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
    subtitle: '전 세계 사서와 평론가가 극찬한 그림책계의 노벨상 수상작',
    title: '칼데콧 수상작',
    tag: '칼데콧',
    slug: 'caldecott',
    category: 'special',
  },
  {
    id: 'special-research',
    subtitle: '실패 없는 책육아를 위한 독서 전문가 100인의 엄선작',
    title: '어린이도서연구회 추천',
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
  iconName: string;
  name: string;
  title: string;
  description: string;
  tags: string[];
}

export const SITUATION_PRESCRIPTIONS: SituationPrescription[] = [
  {
    id: 'all',
    iconName: 'LayoutGrid',
    name: '전체',
    title: '50여 가지 맞춤 큐레이션 서가',
    description: '아이를 위한 모든 맞춤 도서 모음이에요.',
    tags: [],
  },
  {
    id: 'sleep',
    iconName: 'Moon',
    name: '잠자리·수면',
    title: '잠투정 없이 편안한 꿀잠 수면의식',
    description: '포근한 동화로 평온한 밤과 꿀잠을 선물해요.',
    tags: ['잠자리'],
  },
  {
    id: 'habits',
    iconName: 'Sparkles',
    name: '생활습관·청결',
    title: '스스로 깨끗하고 바른 생활습관',
    description: '스스로 실천하는 바른 생활 습관을 익혀요.',
    tags: ['생활습관', '미디어', '경제', '요리', '패션', '신체활동'],
  },
  {
    id: 'self_esteem',
    iconName: 'Heart',
    name: '자존감·자신감',
    title: '기죽지 않고 단단한 마음과 용기',
    description: '포기하지 않는 단단한 마음과 용기를 키워요.',
    tags: ['자존감', '용기', '끈기', '행복'],
  },
  {
    id: 'emotions',
    iconName: 'Smile',
    name: '감정표현·마음',
    title: '벅찬 감정을 다독이고 표현하기',
    description: '다양한 감정을 이해하고 마음을 다독여줘요.',
    tags: ['분노조절', '두려움', '질투', '슬픔', '위로', '용서'],
  },
  {
    id: 'social',
    iconName: 'Users',
    name: '친구·사회성',
    title: '기관 적응과 사이좋은 또래 관계',
    description: '배려와 규칙을 익히며 따뜻한 우정을 쌓아요.',
    tags: ['적응', '사회성', '우정', '배려', '나눔', '규칙', '의사소통'],
  },
  {
    id: 'family',
    iconName: 'Home',
    name: '가족·이웃',
    title: '가장 따뜻한 가족 사랑과 이웃',
    description: '가족의 소중함과 따뜻한 이웃 사랑을 전해요.',
    tags: ['가족사랑', '이웃', '평화'],
  },
  {
    id: 'diversity',
    iconName: 'Globe',
    name: '다양성·존중',
    title: '편견 없이 세상을 품는 넓은 시선',
    description: '서로의 다름을 존중하며 넓은 시선을 배워요.',
    tags: ['다양성', '다문화', '장애', '양성평등'],
  },
  {
    id: 'language',
    iconName: 'BookOpen',
    name: '언어·문해력',
    title: '말놀이 재미와 소중한 우리 한글',
    description: '풍부한 어휘력과 옛이야기 지혜를 배워요.',
    tags: ['한글', '글쓰기', '전래동화', '우리문화'],
  },
  {
    id: 'imagination',
    iconName: 'Lightbulb',
    name: '상상·창의력',
    title: '기발한 상상력과 흥미진진한 모험',
    description: '무한한 상상력과 흥미진진한 모험을 떠나요.',
    tags: ['상상력', '모험', '판타지', '유머', '추리', '하늘', '괴물', '미래상상', '미래도시'],
  },
  {
    id: 'nature',
    iconName: 'Leaf',
    name: '자연·생태',
    title: '초록 지구와 살아 숨 쉬는 자연',
    description: '동식물 친구들과 아름다운 자연을 만나요.',
    tags: ['자연관찰', '동물', '식물', '곤충', '환경보호', '바다', '날씨', '동물도감', '봄', '여름', '가을', '겨울', '생명존중'],
  },
  {
    id: 'science',
    iconName: 'Compass',
    name: '과학·탐구',
    title: '공룡부터 우주까지 신나는 탐구',
    description: '우주와 과학 원리로 탐구 호기심을 채워요.',
    tags: ['공룡', '우주', '인체', '과학원리', '수학', '발명', '인공지능', '코딩', '인문지리'],
  },
  {
    id: 'arts',
    iconName: 'Palette',
    name: '예술·감성',
    title: '풍부한 예술 감성과 아름다운 명화',
    description: '명화와 음악으로 풍부한 예술 감성을 키워요.',
    tags: ['예술감성', '명화', '음악', '연극', '건축', '세계역사', '역사이야기', '명절', '전통놀이', '스포츠'],
  },
  {
    id: 'curated_hall',
    iconName: 'Award',
    name: '교과서·수상작',
    title: '전문가와 교과서가 검증한 필독서',
    description: '교과서 수록도서와 검증된 추천 필독서예요.',
    tags: ['교과서수록', '칼데콧', '어린이도서연구회', '여름방학2026'],
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

