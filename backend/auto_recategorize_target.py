"""
'외국', '외국도서', '학부모' 카테고리 도서를 AI(Gemini)를 사용해 다시 분류하는 스크립트
"""
import asyncio
import aiohttp
import sys
import os
import google.generativeai as genai
from supabase_client import supabase

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except: pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALADIN_TTB_KEY = os.getenv("ALADIN_TTB_KEY")

if not GEMINI_API_KEY or not ALADIN_TTB_KEY:
    print("❌ 환경 변수에 GEMINI_API_KEY 또는 ALADIN_TTB_KEY가 설정되지 않았습니다.")
    sys.exit(1)

# 업데이트된 유효 카테고리 목록 ('외국', '학부모' 제외)
VALID_CATEGORIES = [
    "동화", "자연", "사회", "과학", "전통", "인물", "시", 
    "만화", "예술", "역사", "소설", "모음", "지리"
]

genai.configure(api_key=GEMINI_API_KEY)
# 모델 하드 코딩 (새로운 API 키 권한 문제 방지)
target_model = "models/gemini-2.5-flash"

if not target_model:
    print("❌ 사용 가능한 모델이 없습니다 (API Key 확인 필요)")
    sys.exit(1)

model = genai.GenerativeModel(target_model)
print(f"✅ 사용 모델: {target_model}")

async def get_description(isbn):
    if not isbn: return None
    url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        "ttbkey": ALADIN_TTB_KEY, "itemIdType": "ISBN13" if len(isbn) == 13 else "ISBN",
        "ItemId": isbn, "output": "js", "Version": "20131101", "OptResult": "description"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if "item" in data and len(data["item"]) > 0:
                        return data["item"][0].get("description", "")
    except: pass
    return None

async def categorize(title, author, publisher, description):
    prompt = f"""당신은 어린이 도서 전문 사서입니다. 다음 도서를 정확한 카테고리로 분류해주세요.

## 도서 정보
제목: {title}
저자: {author}
출판사: {publisher}
책 소개: {description[:1000] if description else ""}

## 카테고리 정의 (반드시 이 중 하나로 분류)
- **동화**: 창작 이야기, 단편/전래동화, 우화, 픽션 (외국 번역 동화, 그림책 모두 포함)
- **자연**: 동물, 식물, 생태, 환경, 공룡 등 자연과학 계열
- **과학**: 과학 원리, 실험, 기술, 우주, 발명 (학습만화 중 형태가 과학인 경우 포함)
- **역사**: 한국사, 세계사 (학습만화 중 역사가 주제인 경우 포함)
- **전통**: 한국 전통문화, 명절, 풍속
- **인물**: 위인전, 전기 (국내, 국외 인물 모두 포함)
- **사회**: 사회 현상, 직업, 경제, 법률, 환경 문제, 심리, 가족/육아/소통 (자녀교육서 포함)
- **지리**: 지도, 국가, 지형, 여행
- **예술**: 미술관, 음악, 공연, 취미
- **시**: 동시, 번역시
- **만화**: 내용과 무관한 코믹 단행본 (학습만화는 주제에 따라 과학/역사 등으로 분류)
- **소설**: 긴 장편 소설, 청소년용 문학
- **모음**: 단편 모음집, 명작 모음

## 중요 지침
1. 제목과 책 소개를 참고하여 위 목록 중 가장 적합한 **단어 하나**를 선택하세요.
2. 이전에 존재했던 '외국', '학부모' 카테고리는 더 이상 없습니다. 
   - 외국도서나 번역동화는 주로 '동화', '소설' 등으로 보냅니다.
   - 자녀교육, 부모/자녀 간의 소통, 육아 책은 책의 본질에 따라 '사회'나 다른 적절한 주제를 선택합니다.
3. 결과는 반드시 **단어 하나만 출력**하세요. 어떠한 부연 설명도 하지 마세요.

분류 결과:"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace("'", "").replace('"', "").replace("*", "").split("\n")[0]
        # 부분 일치 보정
        for vc in VALID_CATEGORIES:
            if vc == text or vc in text: return vc
    except Exception as e: 
        print(f"Gemini API Error: {e}")
    return "동화" # 예측 실패시 기본값

async def main():
    try:
        targets = ['외국', '외국도서', '학부모']
        result = supabase.table('childbook_items').select('id,title,author,publisher,isbn,category').in_('category', targets).execute()
        books = result.data
        if not books:
            print("❌ 처리할 대상 도서('외국', '외국도서', '학부모')가 없습니다.")
            return

        print(f"🚀 총 {len(books)}권 재분류 시작...\n")
        
        for i, book in enumerate(books, 1):
            sys.stdout.write(f"[{i:03d}/{len(books):03d}] 기존:[{book['category']}] {book['title'][:20]}... ")
            sys.stdout.flush()
            
            desc = await get_description(book.get('isbn'))
            new_cat = await categorize(book['title'], book.get('author',''), book.get('publisher',''), desc)
            
            try:
                # DB 업데이트
                supabase.table('childbook_items').update({'category': new_cat}).eq('id', book['id']).execute()
                print(f"➡️ {new_cat} (OK)")
            except Exception as e:
                print(f"➡️ {new_cat} (DB Error: {e})")
            
            await asyncio.sleep(2) # 429 방지 (건당 2초)
            
        print("\n✅ 모든 도서 재분류 작업 완료!")
        
    except Exception as e:
        print(f"\n❌ 실행 중 치명적 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
