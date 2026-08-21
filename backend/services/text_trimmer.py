"""
카드뉴스 설명 텍스트 트리밍 유틸리티.

카드뉴스 이미지 내부의 설명글이 3줄(60~70자)에 꽉 차도록 정제하는
두 가지 함수를 제공합니다.
"""


def trim_text_fallback(text: str, max_len: int = 65) -> str:
    """텍스트를 3줄 규격(55~65자)에 알맞게 어절과 문장이 훼손되지 않도록 자연스럽게 다듬습니다."""
    import re
    # 연속 공백 및 줄바꿈 정리
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) <= max_len:
        if not text.endswith(('.', '!', '?')):
            text += '.'
        return text

    # 마침표 기준으로 문장 분할
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    combined = ""
    for s in sentences:
        candidate = (combined + " " + s).strip() + "."
        if len(candidate) <= max_len:
            combined = candidate
        else:
            break
            
    # 첫 문장부터 max_len을 초과하는 경우, 어절(공백) 단위로 안전하게 자르기
    if not combined:
        first_sentence = sentences[0] if sentences else text
        words = first_sentence.split()
        temp = ""
        for w in words:
            if len(temp + " " + w) <= max_len - 8:
                temp = (temp + " " + w).strip()
            else:
                break
        if temp:
            combined = temp + " 이야기입니다."
        else:
            combined = first_sentence[:max_len - 1].rstrip() + "."
            
    # 길이가 너무 짧으면(40자 미만) 2번째 문장을 적절히 요약하거나 보충
    if len(combined) < 40 and len(sentences) > 1:
        second = sentences[1]
        words = second.split()
        temp = combined.rstrip('.')
        for w in words:
            if len(temp + " " + w) <= max_len - 1:
                temp = temp + " " + w
            else:
                break
        combined = temp.strip() + "."

    return combined


def force_trim_description(text: str, max_len: int = 65) -> str:
    """텍스트가 max_len을 초과하는 경우, 어절이 잘리지 않도록 안전하게 완성형으로 트리밍합니다."""
    return trim_text_fallback(text, max_len)
