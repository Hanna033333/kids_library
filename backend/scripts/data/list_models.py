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

print("사용 가능한 모든 모델:")
print("="*60)
for m in genai.list_models():
    print(f"\n모델명: {m.name}")
    print(f"  지원 메서드: {m.supported_generation_methods}")
