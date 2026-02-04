"""
도서 카테고리 분류 헬퍼 (예제 코드)
사용법: import 후 categorize_new_book 함수 호출
"""
import asyncio
import aiohttp
import os
import google.generativeai as genai
from supabase_client import supabase  # 프로젝트 내 supabase_client 사용 권장

# ---------------------------------------------------------
# 설정 (환경 변수 사용)
# ---------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALADIN_TTB_KEY = os.getenv("ALADIN_TTB_KEY")

VALID_CATEGORIES = [
    "동화", "외국", "자연", "사회", "과학", "전통", "인물", "시", 
    "만화", "예술", "역사", "소설", "모음", "학부모", "지리"
]

# Gemini 초기화 (동적 모델 선택)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # gemini-2.0-flash 우선, 없으면 1.5-flash
        model_name = next((m for m in models if 'gemini-2.0-flash' in m), 
                          next((m for m in models if 'gemini-1.5-flash' in m), models[0] if models else None))
        
        if model_name:
            model = genai.GenerativeModel(model_name)
        else:
            model = None
            print("⚠️ 사용 가능한 Gemini 모델을 찾을 수 없습니다.")
    except Exception as e:
        model = None
        print(f"⚠️ Gemini 초기화 실패: {e}")
else:
    model = None
    print("⚠️ GEMINI_API_KEY가 설정되지 않았습니다.")

# ---------------------------------------------------------
# 핵심 함수
# ---------------------------------------------------------

async def get_book_description(isbn: str) -> str:
    """알라딘 API로 책 소개 조회"""
    if not isbn or not ALADIN_TTB_KEY: return None
    
    url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        "ttbkey": ALADIN_TTB_KEY,
        "itemIdType": "ISBN13" if len(isbn) == 13 else "ISBN",
        "ItemId": isbn,
        "output": "js",
        "Version": "20131101",
        "OptResult": "description"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    if "item" in data and len(data["item"]) > 0:
                        return data["item"][0].get("description", "")
    except Exception as e:
        print(f"❌ 알라딘 API 오류: {e}")
    return None

async def categorize_book(title: str, author: str, publisher: str, description: str = None) -> str:
    """Gemini를 사용하여 카테고리 분류"""
    if not model: return "동화" # 모델 없으면 기본값
    
    prompt = f"""당신은 어린이 도서 전문 사서입니다. 다음 도서를 정확한 카테고리로 분류해주세요.

## 도서 정보
제목: {title}
저자: {author}
출판사: {publisher}
책 소개: {description[:1000] if description else "없음"}

## 카테고리 정의 (반드시 이 중 하나로 분류)
- **동화**: 창작 이야기, 전래동화, 우화, 픽션
- **외국**: 외국 작가 번역서 (해리포터 등)
- **자연**: 동물, 식물, 생태, 환경, 공룡
- **과학**: 과학 원리, 기술, 우주, 발명 (Why? 시리즈)
- **역사**: 한국사, 세계사
- **전통**: 한국 전통문화, 민속
- **인물**: 위인전
- **사회**: 사회 문제, 직업, 경제, 법, 정치
- **지리**: 지도, 세계 여러 나라
- **예술**: 미술, 음악
- **시**: 동시
- **만화**: 순수 만화
- **소설**: 장편 소설 (고학년용)
- **모음**: 모음집
- **학부모**: 자녀 교육서

## 중요 지침
1. **가장 적합한 단 하나**의 카테고리만 선택하세요.
2. 결과는 설명 없이 **단어 하나만** 출력하세요.

분류 결과:"""

    try:
        # 비동기 실행을 위해 run_in_executor 사용 (Gemini API는 동기 함수일 수 있음)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, model.generate_content, prompt)
        
        text = response.text.strip().replace("'", "").replace('"', "").replace("*", "").split("\n")[0]
        
        for vc in VALID_CATEGORIES:
            if vc == text or vc in text:
                return vc
                
    except Exception as e:
        print(f"❌ AI 분류 오류: {e}")
        
    return "동화" # 실패 시 기본값

# ---------------------------------------------------------
# 통합 함수
# ---------------------------------------------------------

async def process_new_book(book_data: dict):
    """
    신규 도서 처리 및 카테고리 할당
    book_data: {'id': ..., 'title': ..., 'isbn': ..., ...}
    """
    print(f"📖 처리 중: {book_data.get('title')}")
    
    # 1. 책 소개 가져오기
    desc = await get_book_description(book_data.get('isbn'))
    
    # 2. 카테고리 분류
    category = await categorize_book(
        book_data.get('title'),
        book_data.get('author', ''),
        book_data.get('publisher', ''),
        desc
    )
    
    print(f"  ➡️ 분류 결과: {category}")
    
    # 3. DB 업데이트 (예시)
    if 'id' in book_data:
        try:
            supabase.table('childbook_items').update({
                'category': category,
                # 'description': desc  # 필요한 경우 설명도 저장
            }).eq('id', book_data['id']).execute()
            print("  ✅ 저장 완료")
        except Exception as e:
            print(f"  ❌ 저장 실패: {e}")
    
    return category
