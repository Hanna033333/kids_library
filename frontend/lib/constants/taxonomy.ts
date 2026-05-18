export interface CurationTag {
  id: number;
  subtitle: string;
  title: string;
  tag: string;
}

export const ALL_TAXONOMY: CurationTag[] = [
  { id: 1, subtitle: "오늘 밤도 꿀잠", title: "포근한 잠자리 책", tag: "잠자리" },
  { id: 2, subtitle: "감정이 서툰 아이를 위한", title: "마음 처방전", tag: "감정조절" },
  { id: 3, subtitle: "기 죽지 않는 아이로", title: "자존감 그림책", tag: "자존감" },
  { id: 4, subtitle: '"친구랑 놀고 싶어!"', title: "사회성 기르기", tag: "사회성" },
  { id: 5, subtitle: "내 몸이 궁금한 꼬마 박사님", title: "신비한 우리 몸", tag: "인체" },
  { id: 6, subtitle: "상상력이 팡팡 터지는", title: "판타지 세계", tag: "판타지" },
  { id: 7, subtitle: "초록 지구를 지키는", title: "환경 학교", tag: "환경보호" },
  { id: 8, subtitle: "생명의 소중함을 배우는", title: "동물 친구들", tag: "생명존중" },
  { id: 9, subtitle: "사랑이 퐁퐁 샘솟는", title: "가족 이야기", tag: "가족사랑" },
  { id: 10, subtitle: '"같이 하면 더 즐거워"', title: "나눔과 배려", tag: "배려" },
  { id: 11, subtitle: "겁 많은 아이도 용감하게", title: "두근두근 모험", tag: "모험" },
  { id: 12, subtitle: "지혜와 해학이 담긴", title: "재밌는 옛이야기", tag: "전래동화" },
  { id: 13, subtitle: "감수성을 깨우는", title: "꼬마 예술가", tag: "예술감성" },
  { id: 14, subtitle: "숲속 친구들의 일상", title: "신비한 자연 관찰", tag: "자연관찰" },
  { id: 15, subtitle: "과거로 떠나는 시간 여행", title: "지혜로운 역사", tag: "역사이야기" },
  { id: 16, subtitle: "원리를 깨우치는 재미", title: "꼬마 과학자", tag: "과학원리" },
  { id: 17, subtitle: "다름을 존중하는 아이", title: "세계 시민 학교", tag: "다양성" },
  { id: 18, subtitle: "등원 거부가 사라지는", title: "즐거운 유치원", tag: "적응" },
  { id: 19, subtitle: "우리 문화의 자부심", title: "전통과 유산", tag: "우리문화" },
  { id: 20, subtitle: "시원한 수박과 바다 여행", title: "여름의 추억", tag: "계절" }
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
