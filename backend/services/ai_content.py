"""
Gemini API 기반 스레드 콘텐츠(캡션 + 카드 설명) 생성 서비스.

generate_ai_threads_content()  : 신규 콘텐츠 생성
apply_feedback_with_gemini()   : 관리자 피드백 반영 재생성
generate_fallback_content()    : Gemini 불가 시 로컬 DB 기반 폴백
"""

import json
import re
import urllib.parse
from typing import Optional, List

import google.generativeai as genai

from core.config import GEMINI_API_KEY
from services.text_trimmer import force_trim_description, trim_text_fallback
from services.card_generator import clean_book_title


def remove_hashtags_and_clean(caption: str) -> str:
    """
    본문 캡션에서 다중 해시태그를 정제하되, 스레드 추천 피드 및 검색 랭킹을 위한
    핵심 토픽 태그 최대 2~3개(#잠자리그림책, #그림책추천, #책육아 등)를 깔끔하게 보존합니다.
    """
    # 모든 해시태그 검색
    tags = re.findall(r'#\S+', caption)
    # 본문에서 해시태그 모두 제거
    cleaned = re.sub(r'#\S+', '', caption)
    # 각 줄의 연속 공백 정리 및 strip
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in cleaned.split('\n')]
    cleaned = '\n'.join(lines)
    # 연속 줄바꿈(3개 이상) 정돈
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    
    # 핵심 대표 토픽 태그 최대 2~3개를 끝에 단정하게 복원
    if tags:
        valid_tags = []
        for t in tags:
            clean_t = re.sub(r'[^\w#가-힣]', '', t.strip())
            if clean_t and clean_t not in valid_tags:
                valid_tags.append(clean_t)
        
        # 최대 3개까지만 취함
        selected_tags = valid_tags[-3:] if len(valid_tags) > 3 else valid_tags
        if selected_tags:
            tag_str = " ".join(selected_tags)
            cleaned = f"{cleaned}\n\n{tag_str}".strip()
            
    return cleaned


def normalize_caption_intro(caption: str) -> str:
    """기존 캡션 상단에 존재할 수 있는 고정된 공식 인사말(안녕하세요, 책자리 입니다)을 제거하여 피드 첫 줄 훅(Hook)이 즉시 노출되도록 정리합니다."""
    lines = caption.split('\n')
    if lines and '안녕하세요' in lines[0] and '책자리' in lines[0]:
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
        caption = '\n'.join(lines)
    return caption.strip()


def _get_gemini_model():
    """사용 가능한 Gemini 모델 인스턴스를 반환합니다."""
    genai.configure(api_key=GEMINI_API_KEY)
    for model_name in ("gemini-2.5-flash", "gemini-2.0-flash"):
        try:
            return genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"},
            )
        except Exception:
            continue
    return None


def generate_fallback_content(
    curation_title: str, curation_tag: str, books: List[dict]
) -> dict:
    """Gemini API 호출이 불가할 때 로컬 DB의 도서 소개 및 요약 정보를 정제하여 스마트 폴백 텍스트를 구성합니다."""
    tag_clean = curation_tag.lstrip("#") if curation_tag else "그림책"
    caption = (
        f"도서관에서 30권씩 빌려보다가 결국 반납 못 하고 내돈내산한 그림책.\n\n"
        f"수십만 원짜리 전집보다 이 단행본들이 아이 반응 훨씬 터짐...\n"
        f"아이들은 재밌으면 알아서 책 좋아하게 되어있거든!\n\n"
        f"실패 없는 <{curation_title}> 5권, 이번 주말 도서관 갈 때 저장해두고 찾아봐 📌\n\n"
        f"#{tag_clean} #그림책추천 #책육아"
    )
    caption = normalize_caption_intro(caption)

    card_descriptions = []
    for b in books[:5]:
        raw_desc = b.get("description") or b.get("curation_note") or f"{b.get('title')} 도서입니다."
        card_descriptions.append(trim_text_fallback(raw_desc))

    return {
        "caption": caption,
        "card_descriptions": card_descriptions,
    }


def generate_ai_threads_content(
    curation_title: str, curation_tag: str, books: List[dict]
) -> dict:
    """Gemini API를 사용하여 스레드용 캡션 및 5권 도서의 3줄 요약 설명(각 65자 내외)을 생성합니다."""
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY가 존재하지 않아 스마트 폴백 메커니즘을 작동합니다.")
        return generate_fallback_content(curation_title, curation_tag, books)

    model = _get_gemini_model()
    if not model:
        print("❌ GenerativeModel 생성 실패. 스마트 폴백을 작동합니다.")
        return generate_fallback_content(curation_title, curation_tag, books)

    books_info = [
        {
            "index": idx + 1,
            "title": clean_book_title(b.get("title") or ""),
            "publisher": b.get("publisher"),
            "description": b.get("description") or b.get("curation_note") or "",
        }
        for idx, b in enumerate(books[:5])
    ]

    prompt = f"""
당신은 아동 도서 큐레이션 서비스 '책자리'의 10만 팔로워 육아 인플루언서이자 전문 사서입니다.
아래 도서 목록과 큐레이션 테마 정보를 바탕으로, 스레드(Threads)에서 조회수 10만 이상 터지는 초압축 사이다 캡션(caption)과 각 도서 카드뉴스 이미지용 3줄 요약 설명 5개(card_descriptions)를 생성해 주세요.

[큐레이션 정보]
- 테마 제목: {curation_title}
- 분류 태그: {curation_tag}

[도서 목록 (총 5권)]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 지침 - 10만 바이럴 5대 앵글 지능형 선택 & 초압축 사이다 구어체]
1. 본문 캡션(caption) 작성 지침:
   - **글자 수**: 공백 포함 **180자에서 250자 내외 (초압축 6~8줄)**. 길고 뻔한 에세이 반성문은 절대 금지합니다!
   - **🔥 5대 바이럴 앵글 중 테마에 가장 적합한 1가지를 자율 선택하여 작성**:
     * **[앵글 1: 현실 팩폭 / 사이다형]**
       "솔직히 전집 100만 원어치 살 필요 없음. 도서관에서 이 5권이면 끝남."
       "책만 펴면 3초 만에 도망가던 5세 아이가 웬일로 엉덩이 붙이고 20분 동안 본 책."
     * **[앵글 2: 선배맘/사서 찐 경험 & 권위형]**
       "도서관에서 30권씩 빌려보다가 결국 반납 못 하고 직접 사버린 그림책."
       "우리 집 TV 없앤 지 3년째, 아이가 매일 스스로 뽑아오는 그림책들."
     * **[앵글 3: 상황별 즉각 처방 / 결핍 직격형]**
       "밤 11시까지 안 자고 버티는 4~7세 아이 10분 만에 기절시키는 책."
       "어린이집 등원할 때마다 문 앞에서 우는 아이에게 읽어줬더니 마법처럼 통함."
     * **[앵글 4: 아이들 찐 반응 / 유머형]**
       "엄마가 읽어주다 빵 터지고 아이는 숨넘어가게 웃은 그림책들."
       "아이들은 교훈적인 책보다 이런 엉뚱한 책에 환장하거든..."
     * **[앵글 5: 도서관 대출 꿀팁 / 실패 방지형]**
       "이번 주말 도서관 가기 전에 무조건 저장해둬야 할 4~7세 필독서."
       "도서관 수만 권 중에 뭘 골라야 할지 모르겠다면 그냥 이 5권 집어와!"
   
   - **본문 구성 (6~8줄 초간결 구조)**:
     1. [1~2줄]: 선택한 앵글의 강력한 첫 줄 도파민 훅
     2. [2~3줄]: 짧고 명쾌한 사이다 공감 & 현실 육아 에피소드 (예: "아이들은 재밌으면 알아서 책 좋아하게 되어있거든!")
     3. [1줄]: 테마 소개 (<{curation_title}> 5권 묶어둠!)
     4. [1줄]: 도서관 대출/저장 유도 ("이번 주말 도서관 갈 때 저장해두고 찾아봐 📌")
     5. [빈 줄 후]: 핵심 토픽 태그 2~3개 (`#세부주제 #그림책추천 #책육아`)
   
   - **어조/문체**: **100% 반말 구어체 필수** (~야, ~해봐, ~했어, ~이거든, ~추천해, ~끝남, ~찾아봐).
   - **절대 금지**: 존댓말(~해요, ~하세요, ~입니다) 사용 금지 / 매번 똑같은 고정 인사말 / 장황한 반성문 에세이 / 본문 내 책 제목 나열 / URL / 구걸성 멘트('스하리' 등)

2. 카드뉴스 도서 요약(card_descriptions) 작성 지침:
    - 5권 각각에 대해 각 도서별 3줄 요약 설명 (공백 포함 60자에서 70자 사이, 총 5개).
    - 문장이 뚝뚝 끊기지 않고 앞뒤 문장이 자연스럽게 이어지는 완성형 문장으로 작성.
    - 정중한 존댓말 종결 어미 사용 (반말 금지, "~이야기입니다" 연속 반복 지양).
    - 추천평 배제, 순수 줄거리 요약으로만 구성.

[반환 형식]
반드시 다음 JSON 구조로 응답해야 합니다:
{{
  "caption": "1~2줄 도파민 훅\\n\\n사이다 공감 2~3줄\\n<{curation_title}> 5권 묶어둠!\\n이번 주말 도서관 갈 때 저장해두고 찾아봐 📌\\n\\n#세부주제 #그림책추천 #책육아",
  "card_descriptions": [
    "1번 책의 3줄 요약 (60~70자)",
    "2번 책의 3줄 요약 (60~70자)",
    "3번 책의 3줄 요약 (60~70자)",
    "4번 책의 3줄 요약 (60~70자)",
    "5번 책의 3줄 요약 (60~70자)"
  ]
}}
"""

    try:
        response = model.generate_content(prompt)
        res_data = json.loads(response.text)
        if not res_data.get("caption") or len(res_data.get("card_descriptions", [])) < 5:
            raise ValueError("Invalid response structure")
            
        caption = res_data["caption"].strip()
        caption = remove_hashtags_and_clean(caption)
        caption = normalize_caption_intro(caption)
        res_data["caption"] = caption
        
        res_data["card_descriptions"] = [
            force_trim_description(desc) for desc in res_data.get("card_descriptions", [])
        ]
        return res_data
    except Exception as e:
        print(f"❌ Gemini API 오류 발생: {e}. 스마트 폴백 메커니즘을 작동합니다.")
        return generate_fallback_content(curation_title, curation_tag, books)


async def apply_feedback_with_gemini(
    feedback_text: str,
    old_caption: str,
    old_descriptions: List[str],
    books: List[dict],
) -> Optional[dict]:
    """Gemini API에 기존 텍스트 시안과 관리자의 피드백 내용을 전달하여 텍스트를 정교하게 재생성합니다."""
    if not GEMINI_API_KEY:
        return None

    model = _get_gemini_model()
    if not model:
        return None

    books_info = [
        {
            "index": idx + 1,
            "title": clean_book_title(b.get("title") or ""),
            "publisher": b.get("publisher"),
            "old_description": old_descriptions[idx] if idx < len(old_descriptions) else "",
        }
        for idx, b in enumerate(books[:5])
    ]

    prompt = f"""
당신은 아동 도서 전문 큐레이션 서비스 '책자리'의 10만 팔로워 육아 인플루언서이자 전문 사서입니다.
사용자(관리자)로부터 이전에 작성된 스레드 캡션 및 개별 도서 5권 요약본에 대한 수정 요청(피드백)을 받았습니다.

[사용자 수정 요청 (피드백)]
"{feedback_text}"

[기존 캡션]
"{old_caption}"

[기존 도서 정보 및 이전 요약]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 지침 - 초압축 사이다 구어체]
1. 본문 캡션(caption) 작성 지침:
   - 사용자의 피드백을 반영하되, 반드시 공백 포함 180자에서 250자 내외 초압축 6~8줄 구조(첫 줄 도파민 훅 ➔ 사이다 공감 ➔ 5권 안내 ➔ 도서관 저장 유도 📌 + 끝에 핵심 해시태그 2~3개)를 유지하세요.
   - static 인사말("안녕하세요"), '스하리', '댓글 달아주세요', URL, 본문 내 책 제목 나열은 금지합니다.

2. 카드뉴스 도서 요약(card_descriptions) 작성 지침:
    - 5권 각각에 대해 공백 포함 60자에서 70자 사이 3줄 요약.
    - 정중한 존댓말 종결 어미 사용.

[반환 형식]
반드시 다음 JSON 구조로 응답해야 합니다:
{{
  "caption": "수정 반영된 초압축 6~8줄 캡션\\n\\n#세부주제 #그림책추천 #책육아",
  "card_descriptions": [
    "수정 반영된 1번 책의 3줄 요약 (60~70자)",
    "수정 반영된 2번 책의 3줄 요약 (60~70자)",
    "수정 반영된 3번 책의 3줄 요약 (60~70자)",
    "수정 반영된 4번 책의 3줄 요약 (60~70자)",
    "수정 반영된 5번 책의 3줄 요약 (60~70자)"
  ]
}}
"""

    try:
        response = model.generate_content(prompt)
        res_data = json.loads(response.text)
        if not res_data.get("caption") or len(res_data.get("card_descriptions", [])) < 3:
            raise ValueError("Invalid response structure")
            
        caption = res_data["caption"].strip()
        caption = remove_hashtags_and_clean(caption)
        caption = normalize_caption_intro(caption)
        res_data["caption"] = caption
        
        res_data["card_descriptions"] = [
            force_trim_description(desc) for desc in res_data.get("card_descriptions", [])
        ]
        return res_data
    except Exception as e:
        print(f"❌ Gemini 피드백 수정 중 오류: {e}")
        return None

