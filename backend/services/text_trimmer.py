"""
카드뉴스 설명 텍스트 트리밍 유틸리티.

카드뉴스 이미지 내부의 설명글이 3줄(60~70자)에 꽉 차도록 정제하는
두 가지 함수를 제공합니다.
"""


def trim_text_fallback(text: str) -> str:
    """텍스트를 3줄을 꽉 채우는 60자 ~ 70자 범위의 자연스러운 문장으로 다듬습니다. (문장 완성형 종결 보장)"""
    sentences = text.replace("\r", "").split(".")
    sentences = [s.strip() for s in sentences if s.strip()]

    combined = []
    current_len = 0
    for s in sentences:
        if current_len + len(s) + 1 <= 68:
            combined.append(s + ".")
            current_len += len(s) + 1
        else:
            if not combined:
                combined.append(s[:64] + ".")
            break

    result = " ".join(combined)
    if len(result) < 60:
        # 분량이 다소 짧을 경우 뒤를 메워 3줄을 꽉 채움
        filler = " 아이와 함께 읽으며 따뜻한 감동과 교훈을 배울 수 있는 그림책입니다."
        result = (result + filler)[:68]
        if not result.endswith("."):
            result = result.rstrip(".") + "."

    if not result.endswith("다."):
        result = result[:64] + " 이야기입니다."
    return result


def force_trim_description(text: str, max_len: int = 70) -> str:
    """텍스트가 max_len(70자)을 초과하는 경우, 자연스러운 문장 종결을 보장하며 강제 슬라이싱합니다."""
    text = text.strip()
    if len(text) <= max_len:
        return text

    # 70자 이내에서 가장 뒤에 있는 마침표(".") 위치를 찾음
    sliced = text[:max_len]
    last_dot = sliced.rfind(".")
    if last_dot != -1 and last_dot >= 30:  # 적어도 30자 이상인 유의미한 곳에서 잘라야 함
        result = sliced[:last_dot + 1]
    else:
        # 마침표가 마땅치 않으면 그냥 어절 단위로 자르고 존댓말 종결 적용
        words = sliced.split()
        if len(words) > 1:
            result = " ".join(words[:-1])
        else:
            result = sliced

    # 마침표로 끝나지 않는 경우 마침표 및 존댓말 종결 보정
    result = result.strip().rstrip(".")
    if not result.endswith("다"):
        # 마지막 어절이 "다"가 아니면 안전하게 존댓말로 종결
        if len(result) > (max_len - 10):
            result = result[:max_len - 12] + " 이야기입니다."
        else:
            result = result + " 이야기입니다."
    else:
        result = result + "."

    # 최종 길이 재검증 (혹시나 추가된 문구 때문에 max_len을 초과하는 경우)
    if len(result) > max_len:
        result = result[:max_len - 7] + " 책입니다."
    return result
