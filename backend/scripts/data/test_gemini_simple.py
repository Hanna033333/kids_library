"""
Gemini API 간단 테스트
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env 로드
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"API Key exists: {bool(api_key)}")

if api_key:
    genai.configure(api_key=api_key)
    
    # 사용 가능한 모델 목록 출력
    print("\n[Available Models]")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
            
    try:
        print("\n[Testing gemini-pro]")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, introduce yourself briefly.")
        print(f"Response: {response.text}")
        print("✅ Success!")
    except Exception as e:
        print(f"\n❌ Error with gemini-pro: {e}")
        
    try:
        print("\n[Testing gemini-1.5-flash]")
        # 최근 모델 시도
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, introduce yourself briefly.")
        print(f"Response: {response.text}")
        print("✅ Success with 1.5-flash!")
    except Exception as e:
         print(f"\n❌ Error with gemini-1.5-flash: {e}")
else:
    print("❌ API Key not found in .env")
