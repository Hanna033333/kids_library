"""
디버그 모드: 한 권만 테스트
"""
import os
import sys
import asyncio
import aiohttp
import google.generativeai as genai
from supabase import create_client, Client

def load_env_manual():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, ".env")
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip("'").strip('"')
    return env_vars

env = load_env_manual()
GEMINI_API_KEY = env.get("GEMINI_API_KEY")
ALADIN_TTB_KEY = env.get("ALADIN_TTB_KEY")

VALID_CATEGORIES = [
    "동화", "외국", "자연", "사회", "과학", "전통", "인물", "시", 
    "만화", "예술", "역사", "소설", "모음", "학부모", "지리"
]

# Gemini 초기화
genai.configure(api_key=GEMINI_API_KEY)
print(f"API Key: {GEMINI_API_KEY[:20]}...")

# 모델 확인
print("\n사용 가능한 모델:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  - {m.name}")

# 모델 선택
model = genai.GenerativeModel('gemini-1.5-flash')
print(f"\n선택된 모델: gemini-1.5-flash")

# 테스트
test_title = "Why? 우주"
test_desc = "우주의 신비를 어린이들에게 쉽게 설명하는 과학 학습만화입니다."

prompt = f"""당신은 어린이 도서 전문 사서입니다. 다음 도서를 정확한 카테고리로 분류해주세요.

## 도서 정보
제목: {test_title}
책 소개: {test_desc}

## 카테고리 정의
{', '.join(VALID_CATEGORIES)}

## 중요 지침
- 논픽션인 경우 주제에 맞게 분류하세요.
- 결과는 카테고리명 단어 하나만 출력하세요.

분류 결과:"""

print("\n" + "="*60)
print("프롬프트:")
print("="*60)
print(prompt)
print("="*60)

try:
    print("\nAPI 호출 중...")
    response = model.generate_content(prompt)
    print(f"\n✅ 성공!")
    print(f"Raw 응답: '{response.text}'")
    
    result = response.text.strip().replace("'", "").replace('"', "").split("\n")[0]
    print(f"파싱 결과: '{result}'")
    
    # 매칭 확인
    for vc in VALID_CATEGORIES:
        if vc == result or vc in result:
            print(f"✅ 매칭됨: {vc}")
            break
    else:
        print(f"❌ 매칭 실패 -> 기본값 '동화'")
        
except Exception as e:
    print(f"\n❌ 에러 발생!")
    print(f"타입: {type(e)}")
    print(f"메시지: {e}")
    import traceback
    traceback.print_exc()
