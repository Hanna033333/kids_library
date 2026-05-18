import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_taxonomy(books):
    """Gemini API를 이용해 도서 리스트를 분석하고 20개의 카테고리를 제안합니다."""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    # 도서 데이터 요약 (토큰 절약을 위해 일부만 요약해서 보냄)
    book_summaries = []
    for b in books[:100]:
        summary = f"- {b['title']} ({b['age']}, {b['category']}): {b.get('keywords', '')}"
        book_summaries.append(summary)
    
    data_str = "\n".join(book_summaries)
    
    prompt = f"""
당신은 대한민국 최고의 어린이 도서 큐레이션 전문가이자 UX 전략가입니다.
아래 제공된 100권의 어린이 도서 데이터를 분석하여, 학부모들이 실제 도서관이나 앱에서 책을 찾을 때 가장 매력적으로 느낄만한 **'상황별/발달단계별/주제별 카테고리 20개'**를 제안해주세요.

[데이터 포인트]
{data_str}

[제안 가이드라인]
1. 단순히 '동화', '과학' 같은 딱딱한 장르명이 아니라, 유저의 '문제 해결'이나 '상황'에 맞춘 이름이어야 합니다.
2. 아이의 성장을 돕는 발달 단계(정서, 인지, 사회성 등)를 포함하세요.
3. 총 20개의 카테고리를 뽑아주세요.
4. 각 카테고리별로 '어떤 책들이 포함되는지' 간단한 설명과 함께 리스트업 해주세요.

[출력 형식]
1. [카테고리명]: (설명)
2. [카테고리명]: (설명)
...
20. [카테고리명]: (설명)
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error during analysis: {e}"

if __name__ == "__main__":
    with open('sample_books_for_taxonomy.json', 'r', encoding='utf-8') as f:
        # JSON 문자열을 리스트로 변환 (따옴표 문제 해결)
        raw_data = f.read()
        # 주의: 이전에 print(res.data)로 저장해서 형식이 파이썬 리스트 형태일 수 있음
        # 안전하게 처리하기 위해 ast.literal_eval 사용하거나 JSON 형식을 맞춤
        import ast
        books = ast.literal_eval(raw_data)
        
    print("--- 🤖 20개 핵심 카테고리 추출 분석 시작 ---")
    result = analyze_taxonomy(books)
    print("\n[AI 제안 카테고리 20선]")
    print(result)
    
    # 결과를 파일로 저장
    with open('proposed_taxonomy_20.txt', 'w', encoding='utf-8') as f:
        f.write(result)
