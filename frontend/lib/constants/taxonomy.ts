export interface CurationTag {
  id: number;
  subtitle: string;
  title: string;
  tag: string;
}

export const ALL_TAXONOMY: CurationTag[] = [
  { id: 1, subtitle: "밤마다 안 자려는 우리 아이에게", title: "💤 스르륵 꿀잠을 부르는 그림책", tag: "잠자리" },
  { id: 2, subtitle: "감정 표현이 서툰 아이를 위한", title: "❤️ 내 아이를 위한 마음 처방전", tag: "감정조절" },
  { id: 3, subtitle: "기 죽지 않고 단단하게 자라도록", title: "✨ 용기와 자존감을 높이는 그림책", tag: "자존감" },
  { id: 4, subtitle: "친구랑 더 재미있게 놀고 싶을 때", title: "🤝 첫 사회성을 길러주는 다정한 동화", tag: "사회성" },
  { id: 5, subtitle: "내 몸이 궁금한 꼬마 박사님에게", title: "🧬 신비한 우리 몸 탐험 여행", tag: "인체" },
  { id: 6, subtitle: "상상하는 모든 것이 이루어지는 곳", title: "🦄 호기심을 깨우는 판타지 세계", tag: "판타지" },
  { id: 7, subtitle: "초록 지구와 함께 숨 쉬며 자라요", title: "🌱 내 아이를 위한 생태 환경 학교", tag: "환경보호" },
  { id: 8, subtitle: "작고 소중한 생명의 온기를 배워요", title: "🐶 생명의 소중함을 일깨우는 동물 친구들", tag: "생명존중" },
  { id: 9, subtitle: "세상에서 가장 따뜻한 품", title: "🏡 사랑이 퐁퐁 솟아나는 가족 이야기", tag: "가족사랑" },
  { id: 10, subtitle: "함께 나누면 행복이 두 배가 돼요", title: "🎁 양보와 다정한 배려를 배우는 시간", tag: "배려" },
  { id: 11, subtitle: "겁 많은 우리 아이도 용감하고 씩씩하게", title: "🦁 두근두근 용기를 주는 모험 이야기", tag: "모험" },
  { id: 12, subtitle: "조상들의 지혜와 재치가 가득", title: "🎒 할머니가 들려주듯 구수한 옛이야기", tag: "전래동화" },
  { id: 13, subtitle: "아름다움을 느끼는 눈과 마음을 길러요", title: "🎨 감수성을 풍부하게 만드는 꼬마 예술가", tag: "예술감성" },
  { id: 14, subtitle: "신비한 숲속과 들판의 비밀", title: "🐜 호기심 가득 자연 관찰 일기", tag: "자연관찰" },
  { id: 15, subtitle: "시간을 거슬러 떠나는 배움의 길", title: "👑 지혜와 교훈을 배우는 역사 여행", tag: "역사이야기" },
  { id: 16, subtitle: "세상의 원리를 깨우치는 재미", title: "🔍 생각하는 힘을 기르는 꼬마 과학자", tag: "과학원리" },
  { id: 17, subtitle: "서로 다름을 인정하고 존중하는 아이", title: "🌍 함께 살아가는 세계 시민 학교", tag: "다양성" },
  { id: 18, subtitle: "아침마다 등원을 거부하는 우리 아이에게", title: "🏫 유치원과 학교생활이 즐거워지는 마법", tag: "적응" },
  { id: 19, subtitle: "우리의 뿌리와 전통을 고스란히", title: "🌾 조상들의 슬기와 문화 유산", tag: "우리문화" },
  { id: 20, subtitle: "사계절이 주는 대자연의 아름다움", title: "☀️ 시원한 바다와 여름의 추억", tag: "계절" }
];

// 7권 이상 매칭되어 렌더링에 적합한 태그들 (7-Book Rule 정책 반영, 총 14개)
export const VALID_AI_TAGS = [
  "가족사랑",
  "모험",
  "배려",
  "판타지",
  "사회성",
  "예술감성",
  "자연관찰",
  "과학원리",
  "생명존중",
  "다양성",
  "자존감",
  "역사이야기",
  "감정조절",
  "우리문화"
];

// 노출 가능한 태그들의 전체 객체 추출
export const VALID_TAXONOMY = ALL_TAXONOMY.filter(item => VALID_AI_TAGS.includes(item.tag));
