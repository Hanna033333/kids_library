"""
Gemini API 기반 스레드 콘텐츠(캡션 + 카드 설명) 생성 서비스.

generate_ai_threads_content()  : 신규 콘텐츠 생성
apply_feedback_with_gemini()   : 관리자 피드백 반영 재생성
generate_fallback_content()    : Gemini 불가 시 로컬 DB 기반 폴백
"""

import json
import urllib.parse
from typing import Optional, List

import google.generativeai as genai

from core.config import GEMINI_API_KEY
from services.text_trimmer import force_trim_description, trim_text_fallback


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
    caption = (
        f"오늘의 추천 큐레이션은 <{curation_title}> 입니다.\n\n"
        f"우리 아이에게 꼭 맞는 책들을 엄선하여 소개해 드려요. "
        f"함께 소중한 독서 시간을 가져보는 건 어떨까요?\n\n"
        f"자세한 도서 목록과 정보는 아래 링크에서 확인해 보세요!\n"
        f"🔗 https://checkjari.com/collections/curation/{urllib.parse.quote(curation_tag)}"
    )

    card_descriptions = []
    for b in books:
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
            "title": b.get("title"),
            "publisher": b.get("publisher"),
            "description": b.get("description") or b.get("curation_note") or "",
        }
        for idx, b in enumerate(books)
    ]

    landing_url = f"https://checkjari.com/collections/curation/{urllib.parse.quote(curation_tag)}"
    prompt = f"""
당신은 아동 도서 전문 큐레이션 서비스 '책자리'의 AI 전문 사서입니다.
아래 도서 목록과 큐레이션 테마 정보를 바탕으로, 인스타그램 스레드(Threads)에 발행할 SNS 본문용 캡션(caption)과 각 도서 카드뉴스 이미지 내부에 들어갈 순수한 3줄짜리 책 요약 설명(card_descriptions)을 생성해 주세요.

[큐레이션 정보]
- 테마 제목: {curation_title}
- 분류 태그: {curation_tag}

[도서 목록]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 지침 - 중요]
1. 본문 캡션(caption) 작성 지침:
   - 양육자(부모님)와 깊이 공감하는 다정하고 따뜻한 존댓말 톤앤매너로 작성하세요.
   - 큐레이션 기획 의도와 관련된 공감되는 실제 양육 에피소드(혹은 부모로서 겪는 고민)가 캡션 첫머리에 필수적으로 배치되어야 합니다.
   - 마지막에는 서비스 유입을 위한 상세 랜딩 링크를 반드시 다음 형식으로 포함하세요:
     "🔗 {landing_url}"
   - 맞춤법, 띄어쓰기, 문장 완성도에 오타가 전혀 없도록 철저히 검수하세요.

2. 카드뉴스 도서 요약(card_descriptions) 작성 지침 (비주얼 가이드):
    - **글자 수 정밀 통제**: 각 도서별로 3줄을 거의 꽉 채울 수 있도록 반드시 공백 포함 60자에서 70자 사이의 완성도 있는 텍스트로 작성하세요.
    - **연결성 극대화 (뚝뚝 끊김 절대 금지)**: 명사형 종결이나 단어/구절의 단순 나열을 절대 금지합니다. 문맥이 부드럽고 자연스럽게 한 문장 혹은 두 문장으로 유기적으로 연결된 완성형 글로 작성해 주세요.
    - **존댓말 종결 어미 필수 (반말 금지)**: 반드시 신뢰감을 주는 정중하고 부드러운 존댓말 종결 어미(예: "~이야기입니다.", "~소개해 줍니다.", "~그려내고 있습니다.", "~담고 있습니다.")만 사용하세요.
    - 양육자용 추천평 멘트는 완전히 배제하고, 순수한 책의 줄거리 요약으로만 작성하세요.
    - 꼬리표 기호나 마크다운 기호는 절대 포함하지 마세요.
    - 문장이 끊기거나 말줄임표(...)로 끝나서는 안 됩니다.

[반환 형식]
반드시 다음 JSON 구조로 응답해야 합니다:
{{
  "caption": "스레드 본문에 노출할 캡션 텍스트",
  "card_descriptions": [
    "1번 책의 3줄 줄거리 요약",
    "2번 책의 3줄 줄거리 요약",
    "3번 책의 3줄 줄거리 요약",
    "4번 책의 3줄 줄거리 요약",
    "5번 책의 3줄 줄거리 요약"
  ]
}}
"""

    try:
        response = model.generate_content(prompt)
        res_data = json.loads(response.text)
        if not res_data.get("caption") or len(res_data.get("card_descriptions", [])) < 5:
            raise ValueError("Invalid response structure")
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
        for idx, b in enumerate(books)
    ]

    prompt = f"""
당신은 아동 도서 전문 큐레이션 서비스 '책자리'의 AI 전문 사서입니다.
사용자(관리자)로부터 이전에 작성된 스레드 캡션 및 개별 도서 요약본에 대한 수정 요청(피드백)을 받았습니다.
이를 바탕으로 캡션과 각 도서의 요약을 업데이트해 주세요.

[사용자 수정 요청 (피드백)]
"{feedback_text}"

[기존 캡션]
"{old_caption}"

[기존 도서 정보 및 이전 요약]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 지침 - 중요]
1. 본문 캡션(caption): 피드백 반영, 따뜻한 존댓말 유지, 랜딩 링크 형식 유지, 맞춤법 보정.
2. 카드뉴스 도서 요약(card_descriptions): 피드백 반영, 공백 포함 60~70자, 완성형 존댓말 문장.

[반환 형식]
{{
  "caption": "수정 반영된 스레드 본문 캡션 텍스트",
  "card_descriptions": [
    "수정 반영된 1번 책의 3줄 요약",
    "수정 반영된 2번 책의 3줄 요약",
    "수정 반영된 3번 책의 3줄 요약",
    "수정 반영된 4번 책의 3줄 요약",
    "수정 반영된 5번 책의 3줄 요약"
  ]
}}
"""

    try:
        response = model.generate_content(prompt)
        res_data = json.loads(response.text)
        if not res_data.get("caption") or len(res_data.get("card_descriptions", [])) < 5:
            raise ValueError("Invalid response structure")
        res_data["card_descriptions"] = [
            force_trim_description(desc) for desc in res_data.get("card_descriptions", [])
        ]
        return res_data
    except Exception as e:
        print(f"❌ Gemini 피드백 수정 중 오류: {e}")
        return None
