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
        f"아이에게 책을 읽어줄 때마다 어떤 책을 골라야 할지 늘 막막하고 고민스러웠어요.\n\n"
        f"하루 일과에 지쳐 참지 못하고 잔소리를 쏟아내고는, 잠든 아이 얼굴을 보며 매일 밤 미안함에 마음이 무거웠습니다.\n\n"
        f"그러다 마음을 다잡고 조용히 이 그림책들을 읽어주기 시작했는데요. 신기하게도 며칠 만에 아이가 먼저 책을 품에 꼭 안고 다가오는 마법 같은 순간을 만났습니다.\n\n"
        f"아이 마음에 따뜻한 평온을 선물하는 <{curation_title}> 그림책 3권, 이번 주말 도서관 가실 때 바로 찾으실 수 있게 카드뉴스로 묶어둡니다.\n\n"
        f"오늘 밤 아이와 잠자리에서 함께 펼쳐보세요. 🌙\n\n"
        f"#{tag_clean} #그림책추천 #책육아"
    )
    caption = normalize_caption_intro(caption)

    card_descriptions = []
    for b in books[:3]:
        raw_desc = b.get("description") or b.get("curation_note") or f"{b.get('title')} 도서입니다."
        card_descriptions.append(trim_text_fallback(raw_desc))

    return {
        "caption": caption,
        "card_descriptions": card_descriptions,
    }


def generate_ai_threads_content(
    curation_title: str, curation_tag: str, books: List[dict]
) -> dict:
    """Gemini API를 사용하여 스레드용 캡션 및 3권 도서의 3줄 요약 설명(각 65자 내외)을 생성합니다."""
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
            "title": b.get("title"),
            "publisher": b.get("publisher"),
            "description": b.get("description") or b.get("curation_note") or "",
        }
        for idx, b in enumerate(books[:3])
    ]

    prompt = f"""
당신은 아동 도서 전문 큐레이션 서비스 '책자리'의 AI 전문 사서이자, 다정한 육아 동반자입니다.
아래 도서 목록과 큐레이션 테마 정보를 바탕으로, 인스타그램 스레드(Threads)에 발행할 SNS 본문용 잔잔하고 다정한 일상 고백형 에세이 캡션(caption)과 각 도서 카드뉴스 이미지 내부에 들어갈 순수한 3줄짜리 책 요약 설명(card_descriptions)을 생성해 주세요.

[큐레이션 정보]
- 테마 제목: {curation_title}
- 분류 태그: {curation_tag}

[도서 목록]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 지침 - 자연스러운 구어체 일상 고백 & 부모 위로형 톤앤매너]
1. 본문 캡션(caption) 작성 지침:
   - **글자 수**: 공백 포함 300자에서 380자 내외로 작성하세요. (단락당 최소 2~3문장 이상 충분히 써야 합니다)
   - **문어체 금지 / 현실 구어체 필수**: "마음이 무거워질 때가 있어요" 같은 밋밋한 문어체 대신, 부모가 실제로 머릿속에서 하는 생각을 따옴표로 담은 입말체를 사용하세요.
   - **5단락 스토리텔링 구조** (단락 사이 빈 줄 삽입, 각 단락은 2~3문장 이상):
     - 1단락(훅): 부모의 속마음을 따옴표 인용으로 시작하는 공감 유도 문장
     - 2단락(공감 확장): 1단락의 감정에서 자연스럽게 이어져 아이와의 소박한 일상이나 발견으로 연결
     - 3단락(전환·위로): 2단락의 경험을 통해 부모가 얻은 깨달음 또는 위로로 전환, 이어서 큐레이션 소개
     - 4단락(안내): 도서관에서 바로 찾을 수 있게 카드뉴스로 정리했다는 자연스러운 안내
     - 5단락(마무리): 현실 시간·장소에 맞는 따뜻한 확정형 문장(이모지 1개) + 빈 줄 + 핵심 해시태그 2~3개
   - **단락 간 연결**: 각 단락이 앞 단락의 감정·상황을 이어받아 물처럼 자연스럽게 흘러야 합니다. 갑작스러운 주제 전환 없이 하나의 흐름으로 이어지도록 쓰세요.
   - **마무리 문장 예시** (테마에 맞게 선택):
     - 행복/마음 테마 ➔ "오늘 밤 아이와 따뜻하게 읽어보세요. 🍀"
     - 수면/잠자리 테마 ➔ "오늘 밤 잠자리에서 편안하게 펼쳐보세요. 🌙"
     - 감정/훈육 테마 ➔ "아이와 마음 나눌 때 다정하게 꺼내보세요. 🌿"
     - 도서관/나들이 테마 ➔ "이번 주말 도서관 가실 때 가볍게 찾아보세요. 📌"
   - **절대 금지**: 책 제목·출판사 본문 나열 / 의문문 마무리 / '안녕하세요 책자리입니다' 인사말 / '스하리'·'댓글 달아주세요' 등 마케팅 멘트 / URL

2. 카드뉴스 도서 요약(card_descriptions) 작성 지침:
    - 각 도서별 3줄 요약 설명 (공백 포함 60자에서 70자 사이).
    - 문장이 뚝뚝 끊기지 않고 앞뒤 문장이 자연스럽게 이어지는 완성형 문장으로 작성.
    - 정중한 존댓말 종결 어미 사용 (반말 금지, "~이야기입니다" 반복 금지, 다양한 어미 활용).
    - 추천평 배제, 순수 줄거리 요약으로만 구성.

[반환 형식]
반드시 다음 JSON 구조로 응답해야 합니다:
{{
  "caption": "1단락 훅\\n\\n2단락 공감 확장\\n\\n3단락 위로와 큐레이션 소개\\n\\n4단락 카드뉴스 안내\\n\\n5단락 따뜻한 마무리 🍀\\n\\n#세부주제 #그림책추천 #책육아",
  "card_descriptions": [
    "1번 책의 3줄 요약 (60~70자)",
    "2번 책의 3줄 요약 (60~70자)",
    "3번 책의 3줄 요약 (60~70자)"
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
            "title": b.get("title"),
            "publisher": b.get("publisher"),
            "old_description": old_descriptions[idx] if idx < len(old_descriptions) else "",
        }
        for idx, b in enumerate(books[:3])
    ]

    prompt = f"""
당신은 아동 도서 전문 큐레이션 서비스 '책자리'의 AI 전문 사서이자 육아 선배입니다.
사용자(관리자)로부터 이전에 작성된 스레드 캡션 및 개별 도서 요약본에 대한 수정 요청(피드백)을 받았습니다.

[사용자 수정 요청 (피드백)]
"{feedback_text}"

[기존 캡션]
"{old_caption}"

[기존 도서 정보 및 이전 요약]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 지침 - 롱폼 공감 에세이형 & 상위 노출 2.0]
1. 본문 캡션(caption) 작성 지침:
   - 사용자의 피드백을 반영하되, 반드시 공백 포함 260자에서 330자 내외 5단락 스토리텔링 구조(1단락 훅 - 2단락 속마음 공감 - 3단락 변화 경험담 - 4단락 카드뉴스 3권 안내 - 5단락 확정 마무리 + 끝에 핵심 해시태그 2~3개)를 유지하세요.
   - 5단락 마무리는 질문형 문장을 절대 금지하며, 현실 시간/장소에 부합하는 확정형 문장으로 마쳐야 합니다.
   - static 인사말("안녕하세요"), '스하리', '댓글 달아주세요', URL, 본문 내 책 제목 나열은 금지합니다.

2. 카드뉴스 도서 요약(card_descriptions) 작성 지침:
    - 공백 포함 60자에서 70자 사이 3줄 요약.
    - 정중한 존댓말 종결 어미 사용.

[반환 형식]
반드시 다음 JSON 구조로 응답해야 합니다:
{{
  "caption": "수정 반영된 롱폼 5단락 캡션 텍스트\\n\\n#세부주제 #그림책추천 #책육아",
  "card_descriptions": [
    "수정 반영된 1번 책의 3줄 요약 (60~70자)",
    "수정 반영된 2번 책의 3줄 요약 (60~70자)",
    "수정 반영된 3번 책의 3줄 요약 (60~70자)"
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

