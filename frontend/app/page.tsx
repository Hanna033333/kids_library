import { Metadata } from 'next'
import HomePageClient from '@/components/HomePageClient'
import { getWinterBooks, getResearchCouncilBooks, getBooksByAge, getBooksByTag } from '@/lib/home-api'
import { getCaldecottBooks } from '@/lib/caldecott-api'
import { createClient } from '@/lib/supabase'
import { VALID_TAXONOMY, CurationTag } from '@/lib/constants/taxonomy'

export const revalidate = 86400; // 24시간마다 백그라운드 재검증 (ISR)

export const metadata: Metadata = {
  metadataBase: new URL("https://checkjari.com"),
  alternates: { canonical: '/' },
  title: "책자리 - 상황별 정서 맞춤 우리 아이 그림책 큐레이션",
  description: "아이의 정서적 상태(잠자리, 감정, 사회성 등)와 발달 단계에 딱 맞춘 상황별 도서 큐레이션 플랫폼. 발견한 책의 전국 도서관 소장 여부와 교보문고 바로 구매를 연결해 드립니다.",
  keywords: "어린이 도서 추천, 유아 그림책 큐레이션, 초등 필독서, 칼데콧 수상작, 어린이도서연구회, 연령별 추천도서, 책자리, 어린이 정서 교육, 아이 감정 발달, 상황별 그림책",
  openGraph: {
    title: "책자리 - 상황별 정서 맞춤 우리 아이 그림책 큐레이션",
    description: "아이의 정서적 상태(잠자리, 감정, 사회성 등)와 발달 단계에 딱 맞춘 상황별 도서 큐레이션 플랫폼. 발견한 책의 전국 도서관 소장 여부와 교보문고 바로 구매를 연결해 드립니다.",
    url: "https://checkjari.com",
    images: [
      {
        url: "/logo.png",
        width: 1200,
        height: 630,
        alt: "책자리 로고",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "책자리 - 상황별 정서 맞춤 우리 아이 그림책 큐레이션",
    description: "아이의 정서적 상태(잠자리, 감정, 사회성 등)와 발달 단계에 딱 맞춘 상황별 도서 큐레이션 플랫폼. 발견한 책의 전국 도서관 소장 여부와 교보문고 바로 구매를 연결해 드립니다.",
    images: ["/logo.png"],
  },
};

export default async function HomePage() {
  const supabase = createClient()
  const defaultAge = '4-7'

  // KST (UTC+9) 날짜 구하기
  const now = new Date()
  const kstOffset = 9 * 60 * 60 * 1000
  const kstNow = new Date(now.getTime() + kstOffset)
  const dateStr = kstNow.toISOString().split('T')[0] // "YYYY-MM-DD"

  let selectedTags: CurationTag[];
  const SCHEDULE_TABLE = [
    // 사전 1주 (6/15 ~ 6/21)
    { start: "2026-06-15", end: "2026-06-21", curations: [
      { id: 9, subtitle: "세상에서 가장 따뜻한 품", title: "🏡 따뜻한 가족 사랑", tag: "가족사랑" as any, slug: "family" },
      { id: 11, subtitle: "겁 많은 우리 아이도 용감하고 씩씩하게", title: "🦁 씩씩한 모험 이야기", tag: "모험" as any, slug: "adventure" },
      { id: 5, subtitle: "내 몸이 궁금한 꼬마 박사님에게", title: "🧬 신비한 우리 몸 그림책", tag: "인체" as any, slug: "body" }
    ]},
    // 사전 2주 (6/22 ~ 6/28)
    { start: "2026-06-22", end: "2026-06-28", curations: [
      { id: 6, subtitle: "상상하는 모든 것이 이루어지는 곳", title: "🦄 호기심 가득 판타지", tag: "판타지" as any, slug: "fantasy" },
      { id: 19, subtitle: "우리의 뿌리와 전통을 고스란히", title: "🌾 지혜 가득 문화 유산", tag: "우리문화" as any, slug: "culture" },
      { id: 14, subtitle: "신비한 숲속과 들판의 비밀", title: "🐜 호기심 자연 관찰", tag: "자연관찰" as any, slug: "nature" }
    ]},
    // 1주 (6/29 ~ 7/5)
    { start: "2026-06-29", end: "2026-07-05", curations: [
      { id: 1, subtitle: "밤마다 안 자려는 우리 아이에게", title: "💤 스르륵 꿀잠 그림책", tag: "잠자리" as any, slug: "sleep" },
      { id: 4, subtitle: "친구랑 더 재미있게 놀고 싶을 때", title: "🤝 다정한 첫 사회성", tag: "사회성" as any, slug: "social" },
      { id: 7, subtitle: "초록 지구와 함께 숨 쉬며 자라요", title: "🌱 초록 생태 환경 그림책", tag: "환경보호" as any, slug: "eco" }
    ]},
    // 2주 (7/6 ~ 7/12)
    { start: "2026-07-06", end: "2026-07-12", curations: [
      { id: 3, subtitle: "기 죽지 않고 단단하게 자라도록", title: "✨ 단단한 자존감 그림책", tag: "자존감" as any, slug: "self-esteem" },
      { id: 12, subtitle: "조상들의 지혜와 재치가 가득", title: "🎒 구수한 옛이야기", tag: "전래동화" as any, slug: "folktale" },
      { id: 20, subtitle: "사계절이 주는 대자연의 아름다움", title: "☀️ 사계절의 아름다움 그림책", tag: "계절" as any, slug: "season" }
    ]},
    // 3주 (7/13 ~ 7/19)
    { start: "2026-07-13", end: "2026-07-19", curations: [
      { id: 8, subtitle: "작고 소중한 생명의 온기를 배워요", title: "🐶 사랑스러운 동물 친구들", tag: "생명존중" as any, slug: "animal" },
      { id: 17, subtitle: "서로 다름을 인정하고 존중하는 아이", title: "🌍 열린 마음 다양성 학교", tag: "다양성" as any, slug: "diversity" },
      { id: 13, subtitle: "아름다움을 느끼는 눈과 마음을 길러요", title: "🎨 감성 풍부 꼬마 예술가", tag: "예술감성" as any, slug: "art" }
    ]},
    // 4주 (7/20 ~ 7/26)
    { start: "2026-07-20", end: "2026-07-26", curations: [
      { id: 10, subtitle: "함께 나누면 행복이 두 배가 돼요", title: "🎁 다정한 배려 그림책", tag: "배려" as any, slug: "care" },
      { id: 15, subtitle: "시간을 거슬러 떠나는 배움의 길", title: "👑 지혜로운 역사 이야기", tag: "역사이야기" as any, slug: "history" },
      { id: 9, subtitle: "두려움을 이겨내고 한 걸음 더", title: "🦁 씩씩한 용기 그림책", tag: "용기" as any, slug: "courage" }
    ]},
    // 5주 (7/27 ~ 8/2)
    { start: "2026-07-27", end: "2026-08-02", curations: [
      { id: 2, subtitle: "감정 표현이 서툰 아이를 위한", title: "❤️ 마음 처방전 그림책", tag: "감정조절" as any, slug: "emotion" },
      { id: 10, subtitle: "너와 내가 함께 그리는 예쁜 우정", title: "🤝 다정한 내 친구", tag: "우정" as any, slug: "friendship" },
      { id: 16, subtitle: "세상의 원리를 깨우치는 재미", title: "🔍 호기심 가득 과학 원리", tag: "과학원리" as any, slug: "science" }
    ]},
    // 6주 (8/3 ~ 8/9)
    { start: "2026-08-03", end: "2026-08-09", curations: [
      { id: 18, subtitle: "괜찮다고 말해주는 다정한 위로", title: "🧸 따뜻한 위로 그림책", tag: "위로" as any, slug: "comfort" },
      { id: 11, subtitle: "정직하게 말하는 마음의 힘", title: "💎 바른 마음 정직 그림책", tag: "정직" as any, slug: "honesty" },
      { id: 38, subtitle: "작은 생명 곤충들의 위대한 한살이", title: "🦋 꿈틀꿈틀 곤충 나라", tag: "곤충" as any, slug: "bugs" }
    ]},
    // 7주 (8/10 ~ 8/16)
    { start: "2026-08-10", end: "2026-08-16", curations: [
      { id: 7, subtitle: "새로운 환경에서도 씩씩하고 즐겁게", title: "🏫 유치원과 학교생활", tag: "적응" as any, slug: "school" },
      { id: 12, subtitle: "나눌수록 커지는 행복의 비밀", title: "🎈 기쁨 두 배 나눔 그림책", tag: "나눔" as any, slug: "sharing" },
      { id: 39, subtitle: "광활한 우주와 반짝이는 별의 비밀", title: "🚀 별빛 가득 우주 여행", tag: "우주" as any, slug: "space" }
    ]},
    // 8주 (8/17 ~ 8/23)
    { start: "2026-08-17", end: "2026-08-23", curations: [
      { id: 13, subtitle: "폭발하는 감정을 다스리는 지혜", title: "🔥 화를 가라앉히는 그림책", tag: "분노조절" as any, slug: "anger" },
      { id: 23, subtitle: "함께 사는 사회의 바른 규칙", title: "🚦 약속을 지키는 그림책", tag: "규칙" as any, slug: "rules" },
      { id: 77, subtitle: "포유류부터 조류까지 다양한 동물의 특징", title: "🦁 생생한 동물 도감", tag: "동물도감" as any, slug: "animal-encyclopedia" }
    ]},
    // 9주 (8/24 ~ 8/30)
    { start: "2026-08-24", end: "2026-08-30", curations: [
      { id: 14, subtitle: "눈물 뒤에 찾아오는 마음의 평온", title: "💧 슬픔을 다독이는 그림책", tag: "슬픔" as any, slug: "sadness" },
      { id: 24, subtitle: "지구촌 다양한 이웃들과 함께", title: "🌐 세계 시민 그림책", tag: "다문화" as any, slug: "global" },
      { id: 41, subtitle: "신비하고 풍요로운 바닷속 세상", title: "🐳 푸른 바다 탐험", tag: "바다" as any, slug: "ocean" }
    ]},
    // 10주 (8/31 ~ 9/6)
    { start: "2026-08-31", end: "2026-09-06", curations: [
      { id: 15, subtitle: "내 안의 욕심을 내려놓는 방법", title: "💚 시샘을 지우는 그림책", tag: "질투" as any, slug: "jealousy" },
      { id: 25, subtitle: "내가 좋아하는 일과 다양한 직업", title: "💼 내 꿈을 찾는 그림책", tag: "진로" as any, slug: "jobs" },
      { id: 42, subtitle: "씨앗에서 피어나는 생명의 경이로움", title: "🌿 무럭무럭 초록 식물", tag: "식물" as any, slug: "plants" }
    ]},
    // 11주 (9/7 ~ 9/13)
    { start: "2026-09-07", end: "2026-09-13", curations: [
      { id: 16, subtitle: "어둠 속에서 만나는 새로운 재미", title: "🔦 밤이 무섭지 않은 그림책", tag: "두려움" as any, slug: "fear" },
      { id: 26, subtitle: "올바른 소비 습관과 경제 상식", title: "🪙 현명한 돈 쓰기", tag: "경제" as any, slug: "economy" },
      { id: 43, subtitle: "비와 눈, 바람이 부는 자연 현상", title: "🌧️ 변화무쌍 날씨 탐구", tag: "날씨" as any, slug: "weather" }
    ]},
    // 12주 (9/14 ~ 9/20)
    { start: "2026-09-14", end: "2026-09-20", curations: [
      { id: 17, subtitle: "끝까지 노력하는 씩씩한 발걸음", title: "🏃 포기하지 않는 끈기", tag: "끈기" as any, slug: "patience" },
      { id: 27, subtitle: "마음을 전하는 따뜻한 말 한마디", title: "🗣️ 대화가 즐거운 그림책", tag: "의사소통" as any, slug: "communication" },
      { id: 44, subtitle: "논리적인 사고를 키워주는 알고리즘", title: "💻 생각하는 컴퓨터 코딩", tag: "코딩" as any, slug: "coding" }
    ]},
    // 13주 (9/21 ~ 9/27)
    { start: "2026-09-21", end: "2026-09-27", curations: [
      { id: 18, subtitle: "괜찮다고 말해주는 다정한 위로", title: "🧸 따뜻한 위로 그림책", tag: "위로" as any, slug: "comfort" },
      { id: 28, subtitle: "서로 존중하며 평화롭게 사는 방법", title: "🕊️ 평화를 지키는 그림책", tag: "평화" as any, slug: "peace" },
      { id: 45, subtitle: "미래 과학 기술과 변화할 우리 일상", title: "🤖 로봇과 인공지능", tag: "인공지능" as any, slug: "ai" }
    ]},
    // 14주 (9/28 ~ 10/4)
    { start: "2026-09-28", end: "2026-10-04", curations: [
      { id: 19, subtitle: "소소한 일상에서 찾는 감사의 기쁨", title: "🍀 매일 매일 행복 그림책", tag: "행복" as any, slug: "happiness" },
      { id: 29, subtitle: "장애를 가진 친구와 함께하는 세상", title: "♿ 편견 없는 눈그림책", tag: "장애" as any, slug: "inclusion" },
      { id: 46, subtitle: "숫자와 규칙으로 세상 읽기", title: "🧮 재미있는 수학 놀이", tag: "수학" as any, slug: "math" }
    ]},
    // 15주 (10/5 ~ 10/11)
    { start: "2026-10-05", end: "2026-10-11", curations: [
      { id: 20, subtitle: "갈등을 풀고 서로를 안아주는 마음", title: "🤝 미안해와 괜찮아", tag: "용서" as any, slug: "forgiveness" },
      { id: 30, subtitle: "남녀 성역할 고정관념을 넘어서", title: "🚻 모두를 위한 평등 그림책", tag: "양성평등" as any, slug: "equality" },
      { id: 47, subtitle: "불편함을 해소한 기발한 창의력", title: "💡 세상을 바꾼 위대한 발명", tag: "발명" as any, slug: "invention" }
    ]},
    // 16주 (10/12 ~ 10/18)
    { start: "2026-10-12", end: "2026-10-18", curations: [
      { id: 52, subtitle: "소리의 울림과 아름다운 멜로디", title: "🎵 아름다운 소리와 음악", tag: "음악" as any, slug: "music" },
      { id: 31, subtitle: "서로 돕고 사는 따뜻한 마을 이야기", title: "🏘️ 우리 동네 이웃 사촌", tag: "이웃" as any, slug: "community" },
      { id: 53, subtitle: "몸짓과 말로 자신을 자유롭게 표현하기", title: "🎭 배우들의 무대 연극", tag: "연극" as any, slug: "theater" }
    ]},
    // 17주 (10/19 ~ 10/25)
    { start: "2026-10-19", end: "2026-10-25", curations: [
      { id: 54, subtitle: "지구촌 조상들이 남긴 위대한 유산", title: "🏛️ 세계 역사와 문화", tag: "세계역사" as any, slug: "world-history" },
      { id: 32, subtitle: "미디어를 바르게 사용하는 습관", title: "📱 스마트폰 조절 그림책", tag: "미디어" as any, slug: "media" },
      { id: 55, subtitle: "유명 화가들의 눈부신 그림 감상", title: "🖼️ 미술관에서 만난 명화", tag: "명화" as any, slug: "painting" }
    ]},
    // 18주 (10/26 ~ 11/1)
    { start: "2026-10-26", end: "2026-11-01", curations: [
      { id: 56, subtitle: "사람들의 삶을 담은 다양한 공간", title: "🧱 튼튼한 건축과 집", tag: "건축" as any, slug: "architecture" },
      { id: 63, subtitle: "상상초월 재미와 유쾌한 웃음", title: "🤪 웃음 빵빵 유머 그림책", tag: "유머" as any, slug: "humor" },
      { id: 57, subtitle: "추석과 설날의 따뜻한 가족 문화", title: "🍡 한국의 정겨운 명절", tag: "명절" as any, slug: "holiday" }
    ]},
    // 19주 (11/2 ~ 11/8)
    { start: "2026-11-02", end: "2026-11-08", curations: [
      { id: 58, subtitle: "윷놀이와 제기차기로 기르는 협동심", title: "🪁 민속 전통 놀이 체험", tag: "전통놀이" as any, slug: "traditional-play" },
      { id: 64, subtitle: "스스로 문제를 해결하는 논리적 탐색", title: "🔍 명탐정의 추리 비밀", tag: "추리" as any, slug: "mystery" },
      { id: 59, subtitle: "말과 글의 아름다움과 세종대왕의 뜻", title: "🔤 소중한 우리 한글", tag: "한글" as any, slug: "language" }
    ]},
    // 20주 (11/9 ~ 11/15)
    { start: "2026-11-09", end: "2026-11-15", curations: [
      { id: 60, subtitle: "나만의 생각과 감정을 담은 첫 글쓰기", title: "✍️ 상상 가득 글쓰기", tag: "글쓰기" as any, slug: "writing" },
      { id: 62, subtitle: "상상하는 모든 것이 이루어지는 곳", title: "🦄 호기심 가득 판타지", tag: "판타지" as any, slug: "fantasy" },
      { id: 66, subtitle: "하늘 위를 훨훨 날고 싶은 꼬마 새", title: "✈️ 하늘을 나는 상상", tag: "하늘" as any, slug: "aviation" }
    ]},
    // 21주 (11/16 ~ 11/22)
    { start: "2026-11-16", end: "2026-11-22", curations: [
      { id: 67, subtitle: "스스로 음식을 만들며 느끼는 보람", title: "🍳 맛있는 요리조리", tag: "요리" as any, slug: "cooking" },
      { id: 68, subtitle: "마음에 드는 스타일을 스스로 고르는 법", title: "👗 내 멋진 옷과 패션", tag: "패션" as any, slug: "fashion" },
      { id: 69, subtitle: "자동차와 기차, 배의 다양한 쓰임새", title: "🚂 씽씽 달리는 탈것", tag: "탈것" as any, slug: "vehicles" }
    ]},
    // 22주 (11/23 ~ 11/29)
    { start: "2026-11-23", end: "2026-11-29", curations: [
      { id: 70, subtitle: "스포츠를 통해 배우는 협동과 경쟁", title: "⚽ 튼튼한 신체 스포츠", tag: "스포츠" as any, slug: "sports" },
      { id: 71, subtitle: "무서운 상상을 친근하게 뒤바꾸는 동화", title: "👻 친근한 괴물 친구들", tag: "괴물" as any, slug: "monsters" },
      { id: 72, subtitle: "우리가 살아갈 미래 사회의 다채로운 모습", title: "🏙️ 꿈꾸는 미래 도시", tag: "미래도시" as any, slug: "future-city" }
    ]},
    // 23주 (11/30 ~ 12/6)
    { start: "2026-11-30", end: "2026-12-06", curations: [
      { id: 73, subtitle: "건강하고 활기찬 신체 놀이", title: "🤸 신나게 몸을 움직여요", tag: "신체활동" as any, slug: "physical-activity" },
      { id: 75, subtitle: "스스로 닦고 씻는 건강한 생활 태도", title: "🧼 깨끗하고 올바른 습관", tag: "생활습관" as any, slug: "habit" },
      { id: 74, subtitle: "화산과 지진, 태풍 등 신비한 자연 현상", title: "🌋 자연의 거대한 힘", tag: "자연재해" as any, slug: "natural-disaster" }
    ]},
    // 24주 (12/7 ~ 12/13)
    { start: "2026-12-07", end: "2026-12-13", curations: [
      { id: 77, subtitle: "포유류부터 조류까지 다양한 동물의 특징", title: "🦁 생생한 동물 도감", tag: "동물도감" as any, slug: "animal-encyclopedia" },
      { id: 76, subtitle: "다양한 나라와 기후, 지형 탐험", title: "🗺️ 세계 지도로 떠나는 여행", tag: "인문지리" as any, slug: "geography" },
      { id: 78, subtitle: "상상 속 외계인과 UFO", title: "🛸 상상 속 외계인과 UFO", tag: "미래상상" as any, slug: "future-imagination" }
    ]}
  ];

  const matched = SCHEDULE_TABLE.find(item => dateStr >= item.start && dateStr <= item.end);
  if (matched) {
    selectedTags = matched.curations;
  } else {
    // 7일 단위 시드 계산 (날짜 기반 결정적 랜덤)
    const daysSinceEpoch = Math.floor(now.getTime() / (1000 * 60 * 60 * 24))
    const seed = Math.floor(daysSinceEpoch / 7)

    // LCG(선형합동법) 기반 시드 난수 생성기
    let lcgState = (seed * 1664525 + 1013904223) & 0xffffffff
    const seededRandom = () => {
      lcgState = (lcgState * 1664525 + 1013904223) & 0xffffffff
      return (lcgState >>> 0) / 0x100000000
    }

    // VALID_TAXONOMY 배열 셔플 (Fisher-Yates)
    const shuffledTags = [...VALID_TAXONOMY]
    for (let i = shuffledTags.length - 1; i > 0; i--) {
      const j = Math.floor(seededRandom() * (i + 1))
      ;[shuffledTags[i], shuffledTags[j]] = [shuffledTags[j], shuffledTags[i]]
    }

    // 상위 3개 태그 선택
    selectedTags = shuffledTags.slice(0, 3)
  }


  // 서버 사이드 병렬 데이터 페칭
  const [researchBooks, ageBooks, caldecottBooks, ...dynamicBooks] = await Promise.all([
    getResearchCouncilBooks(7, supabase),
    getBooksByAge(defaultAge, 7, supabase),
    getCaldecottBooks(supabase),
    ...selectedTags.map(t => getBooksByTag(t.tag, 7, supabase))
  ])

  // HomePageClient에 전달할 동적 큐레이션 데이터 구성
  const dynamicCurations = selectedTags.map((tag, index) => ({
    subtitle: tag.subtitle,
    title: tag.title,
    tag: tag.tag,
    books: dynamicBooks[index]
  }))

  return <HomePageClient
    initialCaldecottBooks={caldecottBooks.slice(0, 7)}
    initialResearchBooks={researchBooks}
    initialAgeBooks={ageBooks}
    initialSelectedAge={defaultAge}
    dynamicCurations={dynamicCurations}
  />
}
