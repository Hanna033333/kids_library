export interface CurationSampleData {
  count: number;
  sample_covers: string[];
  sample_titles: string[];
}

export const CURATION_THEME_SAMPLES: Record<string, CurationSampleData> = {
  "caldecott": {
    "count": 11,
    "sample_covers": [
      "https://image.aladin.co.kr/product/13514/88/cover500/8952786483_1.jpg",
      "https://image.aladin.co.kr/product/7848/68/cover500/k252434524_2.jpg"
    ],
    "sample_titles": [
      "시간 상자",
      "위니를 찾아서",
      "쌍둥이 빌딩 사이를 걸어간 남자"
    ]
  },
  "research-council": {
    "count": 42,
    "sample_covers": [
      "https://image.aladin.co.kr/product/23816/95/cover200/8962681900_2.jpg",
      "https://image.aladin.co.kr/product/5970/21/cover200/8954844162_1.jpg"
    ],
    "sample_titles": [
      "한양에서 동래까지",
      "호랑이와 곶감",
      "어린 왕자"
    ]
  },
  "summer-vacation": {
    "count": 39,
    "sample_covers": [
      "https://image.aladin.co.kr/product/37564/79/cover500/k712032523_1.jpg",
      "https://image.aladin.co.kr/product/38268/85/cover500/k742034833_1.jpg"
    ],
    "sample_titles": [
      "지구에 옷이 너무 많다고?",
      "왜? 초등 경제질문 100",
      "윗집에 누가 살까?"
    ]
  },
  "textbook": {
    "count": 197,
    "sample_covers": [
      "https://image.aladin.co.kr/product/30077/82/cover500/k812839374_2.jpg",
      "https://image.aladin.co.kr/product/25151/14/cover500/8954674631_2.jpg"
    ],
    "sample_titles": [
      "나는 안내견이야",
      "5번 레인",
      "꽃에서 나온 코끼리"
    ]
  },
  "가족사랑": {
    "count": 141,
    "sample_covers": [
      "https://image.aladin.co.kr/product/49/78/cover500/8901044870_3.jpg",
      "https://image.aladin.co.kr/product/11467/53/cover500/8936427296_1.jpg"
    ],
    "sample_titles": [
      "앤서니 브라운의 행복한 미술관",
      "개구쟁이 산복이",
      "위니를 찾아서"
    ]
  },
  "모험": {
    "count": 73,
    "sample_covers": [
      "https://image.aladin.co.kr/product/8232/52/cover500/k322434954_1.jpg",
      "https://image.aladin.co.kr/product/4643/1/cover500/8949191415_1.jpg"
    ],
    "sample_titles": [
      "깜빡하고 수도꼭지 안 잠근 날",
      "용감한 달 사냥꾼",
      "찾았다, 곰돌이!"
    ]
  },
  "인체": {
    "count": 15,
    "sample_covers": [
      "https://image.aladin.co.kr/product/11756/37/cover500/k162531927_1.jpg",
      "https://image.aladin.co.kr/product/874/22/cover500/8955821182_1.jpg"
    ],
    "sample_titles": [
      "나만 몰랐던 잠 이야기",
      "우리 몸의 구멍",
      "미래가 온다 바이러스"
    ]
  },
  "판타지": {
    "count": 51,
    "sample_covers": [
      "https://image.aladin.co.kr/product/13514/88/cover500/8952786483_1.jpg",
      "https://image.aladin.co.kr/product/5300/60/cover500/8954634745_1.jpg"
    ],
    "sample_titles": [
      "시간 상자",
      "노잣돈 갚기 프로젝트",
      "땅속 나라 도둑 괴물"
    ]
  },
  "우리문화": {
    "count": 51,
    "sample_covers": [
      "https://image.aladin.co.kr/product/66/4/cover500/8901057409_2.jpg",
      "https://image.aladin.co.kr/product/8/31/cover500/8986565064_2.jpg"
    ],
    "sample_titles": [
      "조선시대 암행어사",
      "손 큰 할머니의 만두 만들기",
      "연이네 설맞이"
    ]
  },
  "자연관찰": {
    "count": 139,
    "sample_covers": [
      "https://image.aladin.co.kr/product/89/4/cover500/8949111799_1.jpg",
      "https://image.aladin.co.kr/product/27/9/cover500/8970940561_2.jpg"
    ],
    "sample_titles": [
      "자작나무 마을 이야기",
      "달님 안녕",
      "비 오는 날 또 만나자"
    ]
  },
  "잠자리": {
    "count": 20,
    "sample_covers": [
      "https://image.aladin.co.kr/product/11756/37/cover500/k162531927_1.jpg",
      "https://image.aladin.co.kr/product/13193/69/cover500/8936455214_1.jpg"
    ],
    "sample_titles": [
      "나만 몰랐던 잠 이야기",
      "이불을 덮기 전에",
      "오늘은 하늘에 둥근 달"
    ]
  },
  "사회성": {
    "count": 93,
    "sample_covers": [
      "https://image.aladin.co.kr/product/10972/55/cover500/8952784022_1.jpg",
      "https://image.aladin.co.kr/product/27478/62/cover500/k452733890_1.jpg"
    ],
    "sample_titles": [
      "세 친구",
      "두 마리 당장 빠져!",
      "둥지 아파트 이사 대작전"
    ]
  },
  "환경보호": {
    "count": 37,
    "sample_covers": [
      "https://image.aladin.co.kr/product/89/4/cover500/8949111799_1.jpg",
      "https://image.aladin.co.kr/product/4683/55/cover500/1195339704_1.jpg"
    ],
    "sample_titles": [
      "자작나무 마을 이야기",
      "코끼리와 숲과 감자칩",
      "GREEN"
    ]
  },
  "자존감": {
    "count": 70,
    "sample_covers": [
      "https://image.aladin.co.kr/product/5044/68/cover500/899250540x_1.jpg",
      "https://image.aladin.co.kr/product/14824/44/cover500/k642532351_1.jpg"
    ],
    "sample_titles": [
      "누가 가장 힘셀까?",
      "여섯 번째 바이올린",
      "딴생각 중"
    ]
  },
  "전래동화": {
    "count": 42,
    "sample_covers": [
      "https://image.aladin.co.kr/product/250/23/cover500/8984285552_1.jpg",
      "https://image.aladin.co.kr/product/4643/1/cover500/8949191415_1.jpg"
    ],
    "sample_titles": [
      "딸랑새",
      "용감한 달 사냥꾼",
      "요술 항아리"
    ]
  },
  "계절": {
    "count": 20,
    "sample_covers": [
      "https://image.aladin.co.kr/product/9355/65/cover500/8911125598_1.jpg",
      "https://image.aladin.co.kr/product/5658/17/cover500/6000839114_1.jpg"
    ],
    "sample_titles": [
      "안녕, 가을",
      "달래네 꽃놀이",
      "눈아이"
    ]
  },
  "생명존중": {
    "count": 68,
    "sample_covers": [
      "https://image.aladin.co.kr/product/89/4/cover500/8949111799_1.jpg",
      "https://image.aladin.co.kr/product/11444/83/cover500/k572531904_1.jpg"
    ],
    "sample_titles": [
      "자작나무 마을 이야기",
      "꼬리의 비밀",
      "코끼리와 숲과 감자칩"
    ]
  },
  "다양성": {
    "count": 53,
    "sample_covers": [
      "https://image.aladin.co.kr/product/33318/85/cover500/k692938584_1.jpg",
      "https://image.aladin.co.kr/product/10438/88/cover500/894911271x_2.jpg"
    ],
    "sample_titles": [
      "룰스",
      "아모스와 보리스",
      "우리는 패배하지 않아"
    ]
  },
  "예술감성": {
    "count": 70,
    "sample_covers": [
      "https://image.aladin.co.kr/product/49/78/cover500/8901044870_3.jpg",
      "https://image.aladin.co.kr/product/6810/65/cover500/896155641x_1.jpg"
    ],
    "sample_titles": [
      "앤서니 브라운의 행복한 미술관",
      "몬드리안을 본 적이 있니?",
      "백다섯 명의 오케스트라"
    ]
  },
  "배려": {
    "count": 81,
    "sample_covers": [
      "https://image.aladin.co.kr/product/11444/83/cover500/k572531904_1.jpg",
      "https://image.aladin.co.kr/product/37900/74/cover500/k132033732_1.jpg"
    ],
    "sample_titles": [
      "꼬리의 비밀",
      "윗집에 누가 살까?",
      "둥지 아파트 이사 대작전"
    ]
  },
  "역사이야기": {
    "count": 19,
    "sample_covers": [
      "https://image.aladin.co.kr/product/21262/81/cover500/8962472031_2.jpg",
      "https://image.aladin.co.kr/product/66/4/cover500/8901057409_2.jpg"
    ],
    "sample_titles": [
      "나는 안중근이다",
      "조선시대 암행어사",
      "운하 옆 오래된 집"
    ]
  },
  "용기": {
    "count": 78,
    "sample_covers": [
      "https://image.aladin.co.kr/product/17915/73/cover500/s122833899_1.jpg",
      "https://image.aladin.co.kr/product/24608/76/cover500/8925540835_1.jpg"
    ],
    "sample_titles": [
      "떨어질까 봐 무서워",
      "모치모치 나무",
      "나는 안중근이다"
    ]
  },
  "감정조절": {
    "count": 48,
    "sample_covers": [
      "https://image.aladin.co.kr/product/17868/60/cover500/k732534731_1.jpg",
      "https://image.aladin.co.kr/product/36888/38/cover500/8955889135_1.jpg"
    ],
    "sample_titles": [
      "눈물빵",
      "나는 오늘도 감정식당에 가요",
      "괴물들이 사는 나라"
    ]
  },
  "우정": {
    "count": 72,
    "sample_covers": [
      "https://image.aladin.co.kr/product/10972/55/cover500/8952784022_1.jpg",
      "https://image.aladin.co.kr/product/7848/68/cover500/k252434524_2.jpg"
    ],
    "sample_titles": [
      "세 친구",
      "위니를 찾아서",
      "아모스와 보리스"
    ]
  },
  "과학원리": {
    "count": 50,
    "sample_covers": [
      "https://image.aladin.co.kr/product/21014/56/cover500/k382636471_1.jpg",
      "https://image.aladin.co.kr/product/18761/16/cover500/k192635378_1.jpg"
    ],
    "sample_titles": [
      "미래가 온다 바이러스",
      "갈라파 행성에서 만난 살아나마스의 진화",
      "가가 씨의 과학 장난감 가게"
    ]
  },
  "상실": {
    "count": 22,
    "sample_covers": [
      "https://image.aladin.co.kr/product/52/50/cover500/8949111381_2.jpg",
      "https://image.aladin.co.kr/product/795/87/cover500/s492636482_1.jpg"
    ],
    "sample_titles": [
      "내가 가장 슬플 때",
      "무릎딱지",
      "조개맨들"
    ]
  },
  "정직": {
    "count": 10,
    "sample_covers": [
      "https://image.aladin.co.kr/product/9123/41/cover500/895828448x_1.jpg",
      "https://image.aladin.co.kr/product/5300/60/cover500/8954634745_1.jpg"
    ],
    "sample_titles": [
      "감기 걸린 물고기",
      "노잣돈 갚기 프로젝트",
      "하멜른의 피리 부는 사나이"
    ]
  },
  "곤충": {
    "count": 7,
    "sample_covers": [
      "https://image.aladin.co.kr/product/9813/40/cover500/k822535954_1.jpg",
      "https://image.aladin.co.kr/product/14231/60/cover500/k822532634_1.jpg"
    ],
    "sample_titles": [
      "머릿니",
      "알아맞혀 봐! 곤충 가면 놀이",
      "꿀벌이 멸종할까 봐"
    ]
  },
  "적응": {
    "count": 45,
    "sample_covers": [
      "https://image.aladin.co.kr/product/29068/10/cover500/k912836553_2.jpg",
      "https://image.aladin.co.kr/product/25151/14/cover500/8954674631_2.jpg"
    ],
    "sample_titles": [
      "간다아아!",
      "5번 레인",
      "겁보 만보"
    ]
  },
  "나눔": {
    "count": 22,
    "sample_covers": [
      "https://image.aladin.co.kr/product/8/31/cover500/8986565064_2.jpg",
      "https://image.aladin.co.kr/product/6022/48/cover500/8998465639_1.jpg"
    ],
    "sample_titles": [
      "손 큰 할머니의 만두 만들기",
      "색깔 손님",
      "사과가 쿵!"
    ]
  },
  "우주": {
    "count": 12,
    "sample_covers": [
      "https://image.aladin.co.kr/product/37772/55/cover500/k112033560_1.jpg",
      "https://image.aladin.co.kr/product/26844/54/cover500/k322730395_1.jpg"
    ],
    "sample_titles": [
      "완다는 별의 소리를 들어요",
      "우리는 우주 어디쯤 있을까?",
      "찾았다! 별자리"
    ]
  },
  "분노조절": {
    "count": 12,
    "sample_covers": [
      "https://image.aladin.co.kr/product/10711/20/cover500/8952782747_1.jpg",
      "https://image.aladin.co.kr/product/11522/57/cover500/8998751232_2.jpg"
    ],
    "sample_titles": [
      "괴물들이 사는 나라",
      "수박이 먹고 싶으면",
      "알도"
    ]
  },
  "규칙": {
    "count": 10,
    "sample_covers": [
      "https://image.aladin.co.kr/product/27478/62/cover500/k452733890_1.jpg",
      "https://image.aladin.co.kr/product/36499/91/cover500/8968308675_1.jpg"
    ],
    "sample_titles": [
      "두 마리 당장 빠져!",
      "엄마 규칙에 반대한다고?",
      "이건 내 모자가 아니야"
    ]
  },
  "공룡": {
    "count": 4,
    "sample_covers": [
      "https://image.aladin.co.kr/product/31606/56/cover500/k162833665_1.jpg",
      "https://image.aladin.co.kr/product/9861/13/cover500/8955823789_1.jpg"
    ],
    "sample_titles": [
      "진짜 진짜 재밌는 공룡 그림책",
      "공룡",
      "공룡은 없어"
    ]
  },
  "슬픔": {
    "count": 29,
    "sample_covers": [
      "https://image.aladin.co.kr/product/52/50/cover500/8949111381_2.jpg",
      "https://image.aladin.co.kr/product/17868/60/cover500/k732534731_1.jpg"
    ],
    "sample_titles": [
      "내가 가장 슬플 때",
      "눈물빵",
      "무릎딱지"
    ]
  },
  "다문화": {
    "count": 4,
    "sample_covers": [
      "https://image.aladin.co.kr/product/10947/40/cover500/8952782925_1.jpg",
      "https://image.aladin.co.kr/product/91/39/cover500/8949111829_2.jpg"
    ],
    "sample_titles": [
      "알도",
      "울타리 너머 아프리카",
      "내 이름은 난민이 아니야"
    ]
  },
  "바다": {
    "count": 5,
    "sample_covers": [
      "https://image.aladin.co.kr/product/14969/17/cover500/k552533967_1.jpg",
      "https://image.aladin.co.kr/product/1/2/cover500/8949110326_2.jpg"
    ],
    "sample_titles": [
      "인어 소녀",
      "고래들의 노래",
      "인어를 믿나요?"
    ]
  },
  "질투": {
    "count": 1,
    "sample_covers": [
      "https://image.aladin.co.kr/product/20566/20/cover500/8943312253_1.jpg"
    ],
    "sample_titles": [
      "앨피가 일등이에요"
    ]
  },
  "진로": {
    "count": 14,
    "sample_covers": [
      "https://image.aladin.co.kr/product/11522/57/cover500/8998751232_2.jpg",
      "https://image.aladin.co.kr/product/7211/22/cover500/8976504690_1.jpg"
    ],
    "sample_titles": [
      "수박이 먹고 싶으면",
      "공부는 왜 해야 하노",
      "안녕, 나의 등대"
    ]
  },
  "식물": {
    "count": 10,
    "sample_covers": [
      "https://image.aladin.co.kr/product/37488/48/cover500/k672032114_1.jpg",
      "https://image.aladin.co.kr/product/26838/61/cover500/8997715755_1.jpg"
    ],
    "sample_titles": [
      "덕분에 발견!",
      "딸기",
      "나무는 좋다"
    ]
  },
  "두려움": {
    "count": 21,
    "sample_covers": [
      "https://image.aladin.co.kr/product/17915/73/cover500/s122833899_1.jpg",
      "https://image.aladin.co.kr/product/22/41/cover500/8949110547_2.jpg"
    ],
    "sample_titles": [
      "떨어질까 봐 무서워",
      "악어도 깜짝, 치과 의사도 깜짝!",
      "시작의 이름"
    ]
  },
  "경제": {
    "count": 12,
    "sample_covers": [
      "https://image.aladin.co.kr/product/31579/42/cover500/k352833767_1.jpg",
      "https://image.aladin.co.kr/product/5744/65/cover500/8968301565_1.jpg"
    ],
    "sample_titles": [
      "무엇일까?",
      "주머니에서 짤랑대는 나의 경제",
      "우리는 돈 벌러 갑니다"
    ]
  },
  "날씨": {
    "count": 5,
    "sample_covers": [
      "https://image.aladin.co.kr/product/29615/70/cover500/k522838273_1.jpg",
      "https://image.aladin.co.kr/product/6752/75/cover500/8998751135_2.jpg"
    ],
    "sample_titles": [
      "구름은 어떻게 구름이 될까?",
      "대추 한 알",
      "바람이 불었어"
    ]
  },
  "끈기": {
    "count": 25,
    "sample_covers": [
      "https://image.aladin.co.kr/product/11050/72/cover500/8983948205_1.jpg",
      "https://image.aladin.co.kr/product/14824/44/cover500/k642532351_1.jpg"
    ],
    "sample_titles": [
      "공기처럼 자유롭게",
      "여섯 번째 바이올린",
      "우리는 패배하지 않아"
    ]
  },
  "의사소통": {
    "count": 26,
    "sample_covers": [
      "https://image.aladin.co.kr/product/37900/74/cover500/k132033732_1.jpg",
      "https://image.aladin.co.kr/product/10497/48/cover500/8932029776_1.jpg"
    ],
    "sample_titles": [
      "윗집에 누가 살까?",
      "임금님의 이사",
      "내가 뉴스를 만든다면?"
    ]
  },
  "코딩": {
    "count": 0,
    "sample_covers": [],
    "sample_titles": []
  },
  "위로": {
    "count": 40,
    "sample_covers": [
      "https://image.aladin.co.kr/product/5044/68/cover500/899250540x_1.jpg",
      "https://image.aladin.co.kr/product/17868/60/cover500/k732534731_1.jpg"
    ],
    "sample_titles": [
      "누가 가장 힘셀까?",
      "눈물빵",
      "이불을 덮기 전에"
    ]
  },
  "평화": {
    "count": 20,
    "sample_covers": [
      "https://image.aladin.co.kr/product/11797/89/cover500/8952783689_1.jpg",
      "https://image.aladin.co.kr/product/36591/25/cover500/k112039653_2.jpg"
    ],
    "sample_titles": [
      "바람이 불 때에",
      "전쟁과 나",
      "왕가리 마타이"
    ]
  },
  "인공지능": {
    "count": 7,
    "sample_covers": [
      "https://image.aladin.co.kr/product/36335/23/cover500/896546742x_1.jpg",
      "https://image.aladin.co.kr/product/25158/89/cover500/k262633474_1.jpg"
    ],
    "sample_titles": [
      "쥐들 G들",
      "로보베이비",
      "미래가 온다 로봇"
    ]
  },
  "행복": {
    "count": 34,
    "sample_covers": [
      "https://image.aladin.co.kr/product/13193/69/cover500/8936455214_1.jpg",
      "https://image.aladin.co.kr/product/6022/48/cover500/8998465639_1.jpg"
    ],
    "sample_titles": [
      "이불을 덮기 전에",
      "색깔 손님",
      "엄마의 의자"
    ]
  },
  "장애": {
    "count": 7,
    "sample_covers": [
      "https://image.aladin.co.kr/product/2/53/cover500/8949110164_2.jpg",
      "https://image.aladin.co.kr/product/30077/82/cover500/k812839374_2.jpg"
    ],
    "sample_titles": [
      "깃털 없는 기러기 보르카",
      "나는 안내견이야",
      "아름다운 아이 줄리안 이야기"
    ]
  },
  "수학": {
    "count": 8,
    "sample_covers": [
      "https://image.aladin.co.kr/product/26/66/cover500/894910072x_1.jpg",
      "https://image.aladin.co.kr/product/11255/53/cover500/8911125822_1.jpg"
    ],
    "sample_titles": [
      "즐거운 이사 놀이",
      "딱 하나 고를게",
      "3 2 1"
    ]
  },
  "용서": {
    "count": 2,
    "sample_covers": [
      "https://image.aladin.co.kr/product/34181/73/cover500/k442931319_1.jpg",
      "https://image.aladin.co.kr/product/87/26/cover500/8952747747_1.jpg"
    ],
    "sample_titles": [
      "너에게 사과하는 방법",
      "고얀 놈 혼내 주기"
    ]
  },
  "양성평등": {
    "count": 4,
    "sample_covers": [
      "https://image.aladin.co.kr/product/9562/85/cover500/k402535233_1.jpg",
      "https://image.aladin.co.kr/product/10947/40/cover500/8952782925_1.jpg"
    ],
    "sample_titles": [
      "돼지책",
      "알도",
      "종이 봉지 공주"
    ]
  },
  "발명": {
    "count": 6,
    "sample_covers": [
      "https://image.aladin.co.kr/product/37488/48/cover500/k672032114_1.jpg",
      "https://image.aladin.co.kr/product/9381/64/cover500/k682535122_1.jpg"
    ],
    "sample_titles": [
      "덕분에 발견!",
      "도마뱀의 발바닥은 신기한 테이프 -자연에서 찾아낸 창의적인 과학기술",
      "비누"
    ]
  },
  "음악": {
    "count": 8,
    "sample_covers": [
      "https://image.aladin.co.kr/product/88/3/cover500/8949111713_2.jpg",
      "https://image.aladin.co.kr/product/12609/16/cover500/8966350763_1.jpg"
    ],
    "sample_titles": [
      "백다섯 명의 오케스트라",
      "나의 첫 오케스트라",
      "여름이 온다"
    ]
  },
  "이웃": {
    "count": 24,
    "sample_covers": [
      "https://image.aladin.co.kr/product/37900/74/cover500/k132033732_1.jpg",
      "https://image.aladin.co.kr/product/10821/49/cover500/k632530558_1.jpg"
    ],
    "sample_titles": [
      "윗집에 누가 살까?",
      "둥지 아파트 이사 대작전",
      "우당탕탕, 할머니 귀가 커졌어요"
    ]
  },
  "연극": {
    "count": 1,
    "sample_covers": [
      "https://image.aladin.co.kr/product/10947/40/cover500/8952782925_1.jpg"
    ],
    "sample_titles": [
      "알도"
    ]
  },
  "세계역사": {
    "count": 7,
    "sample_covers": [
      "https://image.aladin.co.kr/product/34136/19/cover500/8966352030_1.jpg",
      "https://image.aladin.co.kr/product/13538/91/cover500/8983090529_1.jpg"
    ],
    "sample_titles": [
      "운하 옆 오래된 집",
      "제노비아",
      "이희수 선생님이 들려주는 이슬람 제대로 알기"
    ]
  },
  "미디어": {
    "count": 3,
    "sample_covers": [
      "https://image.aladin.co.kr/product/13520/7/cover500/8964963636_1.jpg",
      "https://image.aladin.co.kr/product/12863/71/cover500/k592532182_1.jpg"
    ],
    "sample_titles": [
      "내가 뉴스를 만든다면?",
      "스티브 잡스",
      "브레멘 음악대 따라하기"
    ]
  },
  "명화": {
    "count": 6,
    "sample_covers": [
      "https://image.aladin.co.kr/product/6810/65/cover500/896155641x_1.jpg",
      "https://image.aladin.co.kr/product/26028/75/cover500/8911128414_1.jpg"
    ],
    "sample_titles": [
      "몬드리안을 본 적이 있니?",
      "꿈꾸는 몽상가 달리의 녹아내리는 시계",
      "수박이 먹고 싶으면"
    ]
  },
  "건축": {
    "count": 6,
    "sample_covers": [
      "https://image.aladin.co.kr/product/11522/57/cover500/8998751232_2.jpg",
      "https://image.aladin.co.kr/product/36572/4/cover500/k802039341_1.jpg"
    ],
    "sample_titles": [
      "수박이 먹고 싶으면",
      "창덕궁에 불이 꺼지면",
      "고양이가 데려간 바람의 집 한옥"
    ]
  },
  "유머": {
    "count": 54,
    "sample_covers": [
      "https://image.aladin.co.kr/product/7758/83/cover500/k192434129_1.jpg",
      "https://image.aladin.co.kr/product/10972/55/cover500/8952784022_1.jpg"
    ],
    "sample_titles": [
      "아빠 아빠, 재미있는 이야기 해주세요",
      "세 친구",
      "갈라파 행성에서 만난 살아나마스의 진화"
    ]
  },
  "명절": {
    "count": 7,
    "sample_covers": [
      "https://image.aladin.co.kr/product/8/33/cover500/s872839779_1.jpg",
      "https://image.aladin.co.kr/product/6616/83/cover200/8994975993_2.jpg"
    ],
    "sample_titles": [
      "솔이의 추석 이야기",
      "한가위만 같아라",
      "호랑호랑 호랑이 추석"
    ]
  },
  "전통놀이": {
    "count": 0,
    "sample_covers": [],
    "sample_titles": []
  },
  "추리": {
    "count": 10,
    "sample_covers": [
      "https://image.aladin.co.kr/product/1554/25/cover500/895689793x_1.jpg",
      "https://image.aladin.co.kr/product/3/34/cover500/8971968419_2.jpg"
    ],
    "sample_titles": [
      "위고 카브레",
      "누가 내 머리에 똥 쌌어?",
      "뉴욕 양말 탐정단"
    ]
  },
  "한글": {
    "count": 5,
    "sample_covers": [
      "https://image.aladin.co.kr/product/32517/73/cover500/k402935926_1.jpg",
      "https://image.aladin.co.kr/product/8273/51/cover500/8936454927_1.jpg"
    ],
    "sample_titles": [
      "작전명 말모이, 한글을 지킨 사람들",
      "땍때굴",
      "어린이 훈민정음 1"
    ]
  },
  "글쓰기": {
    "count": 9,
    "sample_covers": [
      "https://image.aladin.co.kr/product/10971/81/cover500/896372235x_1.jpg",
      "https://image.aladin.co.kr/product/10279/10/cover500/k872536184_1.jpg"
    ],
    "sample_titles": [
      "어린이는 어린이다",
      "내가 쓰고 그린 책",
      "일하는 아이들"
    ]
  },
  "상상력": {
    "count": 148,
    "sample_covers": [
      "https://image.aladin.co.kr/product/13514/88/cover500/8952786483_1.jpg",
      "https://image.aladin.co.kr/product/8232/52/cover500/k322434954_1.jpg"
    ],
    "sample_titles": [
      "시간 상자",
      "깜빡하고 수도꼭지 안 잠근 날",
      "상자가 좋아"
    ]
  },
  "하늘": {
    "count": 2,
    "sample_covers": [
      "https://image.aladin.co.kr/product/27/9/cover500/8970940561_2.jpg",
      "https://image.aladin.co.kr/product/23287/52/cover200/8998751461_1.jpg"
    ],
    "sample_titles": [
      "달님 안녕",
      "하늘에"
    ]
  },
  "요리": {
    "count": 6,
    "sample_covers": [
      "https://image.aladin.co.kr/product/287/88/cover500/8993242054_1.jpg",
      "https://image.aladin.co.kr/product/10693/58/cover500/k232530642_1.jpg"
    ],
    "sample_titles": [
      "가을이네 장 담그기",
      "우리 학교 장독대",
      "아빠와 피자놀이"
    ]
  },
  "패션": {
    "count": 2,
    "sample_covers": [
      "https://image.aladin.co.kr/product/7744/28/cover500/8961556495_1.jpg",
      "https://image.aladin.co.kr/product/104/39/cover500/039489861d_1.jpg"
    ],
    "sample_titles": [
      "코코의 리틀 블랙 드레스",
      "안나의 빨간 외투"
    ]
  },
  "탈것": {
    "count": 6,
    "sample_covers": [
      "https://image.aladin.co.kr/product/25522/5/cover500/8998751836_1.jpg",
      "https://image.aladin.co.kr/product/11799/58/cover500/895278376x_1.jpg"
    ],
    "sample_titles": [
      "바빠요, 바빠!",
      "케이티와 폭설",
      "말괄량이 기관차 치치"
    ]
  },
  "스포츠": {
    "count": 1,
    "sample_covers": [
      "https://image.aladin.co.kr/product/34151/17/cover200/8949122065_1.jpg"
    ],
    "sample_titles": [
      "플레이 볼"
    ]
  },
  "괴물": {
    "count": 1,
    "sample_covers": [
      "https://image.aladin.co.kr/product/30995/46/cover500/k272831501_1.jpg"
    ],
    "sample_titles": [
      "여우 요괴"
    ]
  },
  "미래도시": {
    "count": 2,
    "sample_covers": [
      "https://image.aladin.co.kr/product/12178/68/cover500/8952783972_1.jpg",
      "https://image.aladin.co.kr/product/1926/32/cover500/8952766415_1.jpg"
    ],
    "sample_titles": [
      "앵거스와 두 마리 오리",
      "스스와 네루네루"
    ]
  },
  "신체활동": {
    "count": 10,
    "sample_covers": [
      "https://image.aladin.co.kr/product/31292/46/cover500/k632832672_1.jpg",
      "https://image.aladin.co.kr/product/10563/53/cover500/8943310722_1.jpg"
    ],
    "sample_titles": [
      "무엇이든 할 수 있는   손 손 손",
      "눈 코 입",
      "5번 레인"
    ]
  },
  "자연재해": {
    "count": 2,
    "sample_covers": [
      "https://image.aladin.co.kr/product/11799/58/cover500/895278376x_1.jpg",
      "https://image.aladin.co.kr/product/28493/58/cover500/8954684114_1.jpg"
    ],
    "sample_titles": [
      "케이티와 폭설",
      "금순이가 기다립니다"
    ]
  },
  "생활습관": {
    "count": 30,
    "sample_covers": [
      "https://image.aladin.co.kr/product/246/38/cover500/8956052565_1.jpg",
      "https://image.aladin.co.kr/product/11756/37/cover500/k162531927_1.jpg"
    ],
    "sample_titles": [
      "이 닦기 싫어요!",
      "나만 몰랐던 잠 이야기",
      "악어도 깜짝, 치과 의사도 깜짝!"
    ]
  },
  "인문지리": {
    "count": 13,
    "sample_covers": [
      "https://image.aladin.co.kr/product/31105/18/cover500/k532831636_1.jpg",
      "https://image.aladin.co.kr/product/36171/49/cover500/k082038196_1.jpg"
    ],
    "sample_titles": [
      "세계 시민으로 살아가는 어린이를 위한 아프리카 안내서",
      "너 지도 볼 줄 알아?",
      "세상이 궁금하다면 지리책"
    ]
  },
  "동물도감": {
    "count": 23,
    "sample_covers": [
      "https://image.aladin.co.kr/product/29/24/cover500/897094317x_2.jpg",
      "https://image.aladin.co.kr/product/19166/99/cover500/8974784211_1.jpg"
    ],
    "sample_titles": [
      "비 오는 날 또 만나자",
      "안녕, 거미야!",
      "야생 동물은 왜 사라졌을까?"
    ]
  },
  "미래상상": {
    "count": 8,
    "sample_covers": [
      "https://image.aladin.co.kr/product/12869/43/cover500/8962681714_2.jpg",
      "https://image.aladin.co.kr/product/24275/23/cover500/k032630788_1.jpg"
    ],
    "sample_titles": [
      "알렙이 알렙에게",
      "미래가 온다 게놈",
      "내일의 동물원"
    ]
  }
};
