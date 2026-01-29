"""
최종 재분류 스크립트 (검증된 supabase_client + 안정적 설정)
"""
import asyncio
import aiohttp
import sys
import os
import google.generativeai as genai
from supabase_client import supabase

# 윈도우 인코딩 설정
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except: pass

# 환경 변수 (없으면 하드코딩된 값 사용 - 최후의 수단)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # .env 파일 수동 로드 시도
    try:
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    GEMINI_API_KEY = line.split("=", 1)[1].strip().strip("'").strip('"')
                    break
    except: pass

ALADIN_TTB_KEY = os.getenv("ALADIN_TTB_KEY") or "ttbrkdgkssk011716001"

VALID_CATEGORIES = [
    "동화", "외국", "자연", "사회", "과학", "전통", "인물", "시", 
    "만화", "예술", "역사", "소설", "모음", "학부모", "지리"
]

# Gemini 설정
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY를 찾을 수 없습니다!")
    sys.exit(1)
    
genai.configure(api_key=GEMINI_API_KEY)

# 모델 찾기
target_model = None
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in available_models if 'gemini-2.0-flash' in m or 'gemini-1.5-flash' in m), None)
    if not target_model and available_models:
        target_model = available_models[0]
except:
    target_model = "models/gemini-1.5-flash" # fallback

if not target_model:
    print("❌ 사용 가능한 모델이 없습니다 (API Key 확인 필요)")
    sys.exit(1)

model = genai.GenerativeModel(target_model)
print(f"✅ 사용 모델: {target_model}")
print(f"✅ Supabase URL: {supabase.supabase_url[:30]}...")

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

## 카테고리 정의 (반드시 이 중 하나)
- **동화**: 창작 이야기, 전래동화, 우화, 픽션
- **외국**: 외국 작가 번역서
- **자연**: 동물, 식물, 생태, 환경, 공룡
- **과학**: 과학 원리, 기술, 우주, 발명, Why? 시리즈
- **역사**: 한국사, 세계사
- **전통**: 한국 전통문화, 민속
- **인물**: 위인전
- **사회**: 사회 문제, 직업, 경제, 법, 정치
- **지리**: 지도, 세계 여러 나라
- **예술**: 미술, 음악
- **시**: 동시
- **만화**: 순수 만화
- **소설**: 장편 소설
- **모음**: 모음집
- **학부모**: 자녀 교육서

## 중요 지침
1. 제목과 책 소개를 참고하여 가장 적합한 하나를 선택하세요.
2. 결과는 단어 하나만 출력하세요.

분류 결과:"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace("'", "").replace('"', "").replace("*", "").split("\n")[0]
        for vc in VALID_CATEGORIES:
            if vc == text or vc in text: return vc
    except: pass
    return "동화" # 기본값

async def main():
    try:
        result = supabase.table('childbook_items').select('id,title,author,publisher,isbn').eq('curation_tag', '겨울방학2026').execute()
        books = result.data
        if not books:
            print("❌ 처리할 도서가 없습니다.")
            return

        print(f"🚀 총 {len(books)}권 재분류 시작...\n")
        
        for i, book in enumerate(books, 1):
            sys.stdout.write(f"[{i}/{len(books)}] {book['title']}... ")
            sys.stdout.flush()
            
            desc = await get_description(book.get('isbn'))
            cat = await categorize(book['title'], book.get('author',''), book.get('publisher',''), desc)
            
            try:
                supabase.table('childbook_items').update({'category': cat}).eq('id', book['id']).execute()
                print(f"➡️ {cat} (OK)")
            except Exception as e:
                print(f"➡️ {cat} (DB Error: {e})")
            
            await asyncio.sleep(10) # 429 방지
            
        print("\n✅ 모든 작업 완료!")
        
    except Exception as e:
        print(f"\n❌ 실행 중 치명적 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
