import google.generativeai as genai
import os

def load_env():
    env_vars = {}
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip().strip("'").strip('"')
    return env_vars

env = load_env()
genai.configure(api_key=env.get("GEMINI_API_KEY"))

print("테스트 1: 모델명 'gemini-1.5-flash'")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("안녕하세요")
    print(f"✅ 성공: {response.text[:50]}")
except Exception as e:
    print(f"❌ 실패: {e}")

print("\n테스트 2: 모델명 'models/gemini-1.5-flash'")
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    response = model.generate_content("안녕하세요")
    print(f"✅ 성공: {response.text[:50]}")
except Exception as e:
    print(f"❌ 실패: {e}")

print("\n테스트 3: 사용 가능한 모델 목록")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  - {m.name}")
