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
    맨 마지막 단일 대표 토픽 태그 1개(#육아, #그림책 등)는 깔끔하게 보존합니다.
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
    
    # 마지막 대표 토픽 태그 1개만 끝에 단정하게 복원
    if tags:
        single_topic_tag = tags[-1].strip()
        # 토픽 태그 특수문자 정제
        single_topic_tag = re.sub(r'[^\w#가-힣]', '', single_topic_tag)
        if single_topic_tag:
            cleaned = f"{cleaned} {single_topic_tag}".strip()
            
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
        f"우리 아이 도서 선택 고민되실 때 바로 꺼내보세요..ㅎ\n\n"
        f"보자마자 혼자 감탄했던 <{curation_title}> 큐레이션입니다.\n\n"
        f"다음번에 도서관 가실 때 바로 찾아보실 수 있게 3권 정리해 둡니다. 📌 #{tag_clean}"
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
당신은 아동 도서 전문 큐레이션 서비스 '책자리'의 AI 전문 사서입니다.
아래 도서 목록과 큐레이션 테마 정보를 바탕으로, 인스타그램 스레드(Threads)에 발행할 SNS 본문용 초간결 3줄 캡션(caption)과 각 도서 카드뉴스 이미지 내부에 들어갈 순수한 3줄짜리 책 요약 설명(card_descriptions)을 생성해 주세요.

[큐레이션 정보]
- 테마 제목: {curation_title}
- 분류 태그: {curation_tag}

[도서 목록]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 지침 - 초간결 저마찰 솔루션 확정형 & 상위 노출 2.0]
1. 본문 캡션(caption) 작성 지침:
   - **글자 수 및 라인 수 엄격 제어**: 본문 캡션은 반드시 공백 포함 100자에서 130자 이내, 정확히 3줄(3문장)로 작성하세요. (모바일 피드에서 '더보기' 클릭 없이 한눈에 들어오는 초간결 분량)
   - **반드시 다음 3행 구조를 엄격히 준수하여 행간 개행(빈 줄)까지 맞춰 생성하세요:**
     1행: [피드 스크롤을 멈추게 하는 강력한 육아 에피소드/상황 1st 라인 훅 (예: "밤마다 안 자고 떼쓰는 4세.. 이 그림책 읽어주고 3일 만에 9시 꿀잠 성공했네요..ㅎ")]
     (빈 줄)
     2행: [3장 카드뉴스 도서 솔루션을 소개하는 감성 공감 문장 (예: "어제도 불 끄니 눈이 초롱초롱하길래 수면 정서 동화 3권 읽어줬더니 스르륵 잠듭니다.")]
     (빈 줄)
     3행: [현실 육아 상황(시간/장소)에 100% 부합하는 솔루션 가치 확정 1줄 + 끝에 대표 단일 토픽 태그 1개 (질문 절대 금지, 이모지 1개 포함)]
          - 수면/잠자리 테마 ➔ "오늘 밤 아이와 잠자리에서 함께 읽어보시면 참 편안해지실 거예요. 🌙 #그림책"
          - 도서관/대출/나들이 테마 ➔ "다음번에 도서관 가실 때 바로 찾아보실 수 있게 3권 정리해 둡니다. 📌 #도서관" 또는 "주말에 아이와 도서관 나들이 가실 때 꺼내보시라고 3권 모아둡니다. 📌 #육아"
   - **질문 종결 절대 금지**: 캡션 마지막 문장은 의문문(? 질문)으로 끝내지 마세요. 카드뉴스로 이미 솔루션을 주었으므로 단정하고 정중한 확정형 문장으로 마쳐야 합니다.
   - **댓글 구걸 및 마케팅 멘트 금지**: '스하리', '댓글 달아주세요', '비밀 링크' 등의 상업적 문구는 절대로 금지합니다.
   - **토픽 태그 제한**: 본문 끝의 단 1개 대표 토픽 태그 외에 해시태그 남발은 절대 금지합니다.
   - **기타 금지 사항**: '안녕하세요, 책자리 입니다' 인사말 금지, URL 링크 금지, 책 제목/출판사명 직접 노출 금지.

2. 카드뉴스 도서 요약(card_descriptions) 작성 지침:
    - 각 도서별 3줄 요약 설명(공백 포함 60자에서 70자 사이).
    - 뚝뚝 끊기지 않고 부드럽게 이어지는 완성형 문장.
    - 정중한 존댓말 종결 어미 적용 (반말 금지, "~이야기입니다" 무한 반복 금지, 다양한 어미 사용).
    - 추천평 배제, 순수 줄거리 요약으로만 구성.

[반환 형식]
반드시 다음 JSON 구조로 응답해야 합니다:
{{
  "caption": "1행 훅\\n\\n2행 솔루션 소개\\n\\n3행 솔루션 확정 1줄 마무리 #토픽태그",
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
당신은 아동 도서 전문 큐레이션 서비스 '책자리'의 AI 전문 사서입니다.
사용자(관리자)로부터 이전에 작성된 스레드 캡션 및 개별 도서 요약본에 대한 수정 요청(피드백)을 받았습니다.

[사용자 수정 요청 (피드백)]
"{feedback_text}"

[기존 캡션]
"{old_caption}"

[기존 도서 정보 및 이전 요약]
{json.dumps(books_info, ensure_ascii=False, indent=2)}

[작성 지침 - 초간결 저마찰 솔루션 확정형 & 상위 노출 2.0]
1. 본문 캡션(caption) 작성 지침:
   - 사용자의 피드백을 반영하되, 반드시 공백 포함 100자에서 130자 이내 초간결 3줄 구조(1행 훅 - 2행 솔루션 소개 - 3행 솔루션 확정 1줄 마무리 + 끝에 단일 토픽 태그 1개)를 유지하세요.
   - 3행 마무리는 질문형 문장을 절대 금지하며, 현실 시간/장소(잠자리 ➔ "오늘 밤 아이와 잠자리에서.. 🌙 #그림책", 도서관 ➔ "다음번에 도서관 가실 때.. 📌 #육아")에 부합하는 확정형 문장으로 마쳐야 합니다.
   - static 인사말("안녕하세요"), '스하리', '댓글 달아주세요', URL, 다중 해시태그 남발, 책 제목 노출은 금지합니다.

2. 카드뉴스 도서 요약(card_descriptions) 작성 지침:
    - 공백 포함 60자에서 70자 사이 3줄 요약.
    - 정중한 존댓말 종결 어미 사용.

[반환 형식]
반드시 다음 JSON 구조로 응답해야 합니다:
{{
  "caption": "수정 반영된 초간결 3줄 캡션 텍스트 #토픽태그",
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

