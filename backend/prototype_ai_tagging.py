import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
ALADIN_TTB_KEY = os.getenv("ALADIN_TTB_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def fetch_book_details(isbn):
    """알라딘 API를 이용해 도서 상세 정보(소개글 포함)를 가져옵니다."""
    url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        'ttbkey': ALADIN_TTB_KEY,
        'itemIdType': 'ISBN13',
        'ItemId': isbn,
        'output': 'js',
        'Version': '20131101',
        'OptResult': 'description'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'item' in data and len(data['item']) > 0:
            item = data['item'][0]
            return {
                'title': item.get('title'),
                'author': item.get('author'),
                'description': item.get('description')
            }
    except Exception as e:
        print(f"Error fetching data from Aladin: {e}")
    return None

def generate_ai_tags(title, description):
    """Gemini API를 이용해 도서 내용을 분석하고 태그와 큐레이션 포인트를 생성합니다."""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    prompt = f"""
당신은 15년 차 베테랑 어린이 도서 사서이자 큐레이션 전문가입니다.
아래 도서 정보를 바탕으로 학부모들이 좋아할 만한 '상황별/감정별 태그' 3~5개와 짧은 '추천 이유(큐레이션 포인트)'를 작성해주세요.

[도서 정보]
제목: {title}
내용 요약: {description}

[태그 후보 예시]
#잠자리독서, #친구관계, #용기, #자존감, #새학기, #배려, #창의력, #감정조절, #사회성, #자연관찰, #생활습관

[출력 형식]
태그: #태그1, #태그2, #태그3
추천 이유: (한 문장으로 핵심만)
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating tags: {e}"

if __name__ == "__main__":
    # 테스트용 도서: "모두 잘 자요" (ISBN13: 9791160269802)
    test_isbn = "9791160269802"
    
    print(f"--- 🔍 도서 정보 조회 중 (ISBN: {test_isbn}) ---")
    book = fetch_book_details(test_isbn)
    
    if book:
        print(f"제목: {book['title']}")
        print(f"작가: {book['author']}")
        print(f"소개글 일부: {book['description'][:100]}...")
        
        print("\n--- 🤖 AI 자동 태깅 분석 시작 ---")
        result = generate_ai_tags(book['title'], book['description'])
        print("\n[AI 분석 결과]")
        print(result)
    else:
        print("도서 정보를 찾을 수 없습니다.")
