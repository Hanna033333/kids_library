import datetime

ALL_TAXONOMY = [
    { "id": 1, "subtitle": "밤마다 안 자려는 우리 아이에게", "title": "💤 스르륵 꿀잠 그림책", "tag": "잠자리", "slug": "sleep" },
    { "id": 2, "subtitle": "감정 표현이 서툰 아이를 위한", "title": "❤️ 마음 처방전 그림책", "tag": "감정조절", "slug": "emotion" },
    { "id": 3, "subtitle": "기 죽지 않고 단단하게 자라도록", "title": "✨ 단단한 자존감 그림책", "tag": "자존감", "slug": "self-esteem" },
    { "id": 4, "subtitle": "친구랑 더 재미있게 놀고 싶을 때", "title": "🤝 다정한 첫 사회성", "tag": "사회성", "slug": "social" },
    { "id": 5, "subtitle": "내 몸이 궁금한 꼬마 박사님에게", "title": "🧬 신비한 우리 몸 그림책", "tag": "인체", "slug": "body" },
    { "id": 6, "subtitle": "상상하는 모든 것이 이루어지는 곳", "title": "🦄 호기심 가득 판타지", "tag": "판타지", "slug": "fantasy" },
    { "id": 7, "subtitle": "초록 지구와 함께 숨 쉬며 자라요", "title": "🌱 초록 생태 환경 그림책", "tag": "환경보호", "slug": "eco" },
    { "id": 8, "subtitle": "작고 소중한 생명의 온기를 배워요", "title": "🐶 사랑스러운 동물 친구들", "tag": "생명존중", "slug": "animal" },
    { "id": 9, "subtitle": "세상에서 가장 따뜻한 품", "title": "🏡 따뜻한 가족 사랑", "tag": "가족사랑", "slug": "family" },
    { "id": 10, "subtitle": "함께 나누면 행복이 두 배가 돼요", "title": "🎁 다정한 배려 그림책", "tag": "배려", "slug": "care" },
    { "id": 11, "subtitle": "겁 많은 우리 아이도 용감하고 씩씩하게", "title": "🦁 씩씩한 모험 이야기", "tag": "모험", "slug": "adventure" },
    { "id": 12, "subtitle": "조상들의 지혜와 재치가 가득", "title": "🎒 구수한 옛이야기", "tag": "전래동화", "slug": "folktale" },
    { "id": 13, "subtitle": "아름다움을 느끼는 눈과 마음을 길러요", "title": "🎨 감성 풍부 꼬마 예술가", "tag": "예술감성", "slug": "art" },
    { "id": 14, "subtitle": "신비한 숲속과 들판의 비밀", "title": "🐜 호기심 자연 관찰", "tag": "자연관찰", "slug": "nature" },
    { "id": 15, "subtitle": "시간을 거슬러 떠나는 배움의 길", "title": "👑 지혜로운 역사 이야기", "tag": "역사이야기", "slug": "history" },
    { "id": 16, "subtitle": "세상의 원리를 깨우치는 재미", "title": "🔍 호기심 가득 과학 원리", "tag": "과학원리", "slug": "science" },
    { "id": 17, "subtitle": "서로 다름을 인정하고 존중하는 아이", "title": "🌍 열린 마음 다양성 학교", "tag": "다양성", "slug": "diversity" },
    { "id": 18, "subtitle": "아침마다 등원을 거부하는 우리 아이에게", "title": "🏫 유치원과 학교 적응", "tag": "적응", "slug": "school" },
    { "id": 19, "subtitle": "우리의 뿌리와 전통을 고스란히", "title": "🌾 지혜 가득 문화 유산", "tag": "우리문화", "slug": "culture" },
    { "id": 20, "subtitle": "사계절이 주는 대자연의 아름다움", "title": "☀️ 사계절의 아름다움 그림책", "tag": "계절", "slug": "season" },
    { "id": 21, "subtitle": "상실과 이별을 다독이는", "title": "🩹 상실과 이별을 다독이는 그림책", "tag": "상실", "slug": "loss" }
]

VALID_AI_TAGS = [
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
    "우리문화",
    "상실"
]

VALID_TAXONOMY = [item for item in ALL_TAXONOMY if item["tag"] in VALID_AI_TAGS]

def get_weekly_curations(now_date: datetime.date = None) -> list:
    """
    프론트엔드와 100% 동일한 LCG 및 Fisher-Yates 셔플 방식을 사용하여
    지정된 날짜(기본: 현재 UTC 기준)에 해당하는 주간 dynamic 큐레이션 3개를 계산합니다.
    """
    if now_date is None:
        # UTC 기준 현재 시각 획득
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_date = now_utc.date()
        
    # Unix epoch (1970-01-01)로부터의 일수 계산
    epoch = datetime.date(1970, 1, 1)
    days_since_epoch = (now_date - epoch).days
    
    # 7일 단위 시드 계산
    seed = days_since_epoch // 7
    
    # LCG(선형합동법) 기반 시드 난수 생성기 - 프론트엔드와 완벽 대칭
    lcg_state = (seed * 1664525 + 1013904223) & 0xffffffff
    
    def seeded_random():
        nonlocal lcg_state
        lcg_state = (lcg_state * 1664525 + 1013904223) & 0xffffffff
        return (lcg_state & 0xffffffff) / 0x100000000

    # Fisher-Yates 셔플
    shuffled = list(VALID_TAXONOMY)
    for i in range(len(shuffled) - 1, 0, -1):
        j = int(seeded_random() * (i + 1))
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        
    return shuffled[:3]
