"""
간단 재분류 스크립트 (검증된 supabase_client 사용)
"""
import asyncio
import aiohttp
import google.generativeai as genai
from supabase_client import supabase
import os

# 환경 변수
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyDYgxS07vtdIjW0lpHDfYjxevehkd_Yhqw"
ALADIN_TTB_KEY = os.getenv("ALADIN_TTB_KEY") or "ttbrkdgkssk011716001"

VALID_CATEGORIES = [
    "동화", "외국", "자연", "사회", "과학", "전통", "인물", "시", 
    "만화", "예술", "역사", "소설", "모음", "학부모", "지리"
]

# Gemini 초기화
genai.configure(api_key=GEMINI_API_KEY)

# 모델 선택
available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
target_model = next((m for m in available_models if 'gemini-2.0-flash' in m or 'gemini-1.5-flash' in m), available_models[0] if available_models else None)

if not target_model:
    print("❌ 사용 가능한 모델이 없습니다!")
    exit(1)

model = genai.GenerativeModel(target_model)
print(f"✅ 모델: {target_model}\n")

async def get_description(isbn):
    if not isbn:
        return None
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
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if "item" in data and len(data["item"]) > 0:
                        return data["item"][0].get("description", "")
    except:
        pass
    return None

async def categorize(title, author, publisher, description):
    prompt = f"""당신은 어린이 도서 전문 사서입니다. 다음 도서를 정확한 카테고리로 분류해주세요.

## 도서 정보
제목: {title}
저자: {author}
출판사: {publisher}
책 소개: {description[:1000] if description else ""}

## 카테고리 정의 (반드시 이 중 하나로 분류)

- **동화**: 창작 이야기, 전래동화, 우화, 픽션 스토리
- **외국**: 외국 작가의 번역서, 외국 문화 소개
- **자연**: 동물, 식물, 생태, 환경, 공룡
- **과학**: 과학 원리, 실험, 기술, 우주, 발명 (Why? 시리즈 포함)
- **역사**: 한국사, 세계사, 역사적 사건
- **전통**: 한국 전통문화, 민속놀이
- **인물**: 위인전, 인물 이야기
- **사회**: 사회 문제, 직업, 경제, 법, 정치
- **지리**: 지도, 세계 여러 나라, 지형
- **예술**: 미술, 음악, 공연
- **시**: 동시, 시집
- **만화**: 순수 만화
- **소설**: 장편 소설
- **모음**: 여러 이야기 모음집
- **학부모**: 자녀 교육서 (부모용)

## 중요 지침
1. 제목과 책 소개를 모두 고려하여 가장 적합한 카테고리를 선택하세요
2. 결과는 카테고리명 단어 하나만 출력하세요 (설명 없이)

분류 결과:"""

    try:
        response = model.generate_content(prompt)
        result = response.text.strip().replace("'", "").replace('"', "").split("\n")[0]
        
        for vc in VALID_CATEGORIES:
            if vc == result or vc in result:
                return vc
        return "동화"
    except:
        return "동화"

async def main():
    # 겨울방학 도서 조회
    result = supabase.table('childbook_items').select(
        'id,title,author,publisher,isbn,category'
    ).eq('curation_tag', '겨울방학2026').execute()
    
    books = result.data
    total = len(books)
    
    print(f"총 {total}권 처리 시작\n")
    
    for i, book in enumerate(books, 1):
        print(f"[{i}/{total}] {book['title']}")
        
        # 책 소개
        desc = await get_description(book.get('isbn'))
        
        # 분류
        category = await categorize(
            book['title'],
            book.get('author', ''),
            book.get('publisher', ''),
            desc
        )
        
        print(f"  → {category}")
        
        # DB 업데이트
        try:
            supabase.table('childbook_items').update({
                'category': category
            }).eq('id', book['id']).execute()
            print(f"  ✅ 저장 완료\n")
        except Exception as e:
            print(f"  ❌ 저장 실패: {e}\n")
        
        await asyncio.sleep(10)  # 429 방지
    
    print(f"\n완료: {total}권 처리")

if __name__ == "__main__":
    asyncio.run(main())
