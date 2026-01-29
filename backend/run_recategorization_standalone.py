"""
겨울방학2026 도서 일괄 재분류 (Fully Standalone)
외부 모듈 의존성 없이 모든 로직을 포함
"""
import asyncio
import os
import sys
import aiohttp
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# 0. 환경 변수 로드 (수동)
# ==========================================
def load_env_manual():
    # 파일 경로 찾기
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, ".env")
    
    if not os.path.exists(env_path):
        # 상위 디렉토리도 확인
        env_path = os.path.join(os.path.dirname(current_dir), ".env")
    
    env_vars = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        # 따옴표 제거 및 공백 정리
                        key = key.strip()
                        value = value.strip().strip("'").strip('"')
                        env_vars[key] = value
        except Exception as e:
            print(f"ERROR reading .env: {e}")
    return env_vars

env = load_env_manual()
GEMINI_API_KEY = env.get("GEMINI_API_KEY")
ALADIN_TTB_KEY = env.get("ALADIN_TTB_KEY")
SUPABASE_URL = env.get("SUPABASE_URL")
SUPABASE_KEY = env.get("SUPABASE_KEY")

# ==========================================
# 1. 설정 및 초기화
# ==========================================

print("=" * 80)
print("초기화 중...")
print(f"GEMINI_KEY Found: {bool(GEMINI_API_KEY)}")
print(f"ALADIN_KEY Found: {bool(ALADIN_TTB_KEY)}")
print(f"SUPABASE URL: {SUPABASE_URL[:10]}..." if SUPABASE_URL else "MISSING")
print("=" * 80)

# Supabase 클라이언트 생성
try:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase creds missing")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"CRITICAL: Supabase Init Failed: {e}")
    sys.exit(1)

# Gemini 설정 및 모델 자동 선택
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    print("🤖 사용 가능한 Gemini 모델 검색 중...")
    target_model_name = None
    
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"   - 발견: {m.name}")
                # 선호 모델 우선순위
                if 'gemini-1.5-flash' in m.name:
                    target_model_name = m.name
                    break
                if 'gemini-pro' in m.name and not target_model_name:
                    target_model_name = m.name
        
        if not target_model_name:
            # 리스트에서 못 찾았으면 기본값 시도
            print("   ⚠️ 모델 리스트에서 적절한 모델을 찾지 못했습니다. 기본값 사용 시도.")
            target_model_name = 'gemini-pro'
            
        print(f"👉 선택된 모델: {target_model_name}")
        model = genai.GenerativeModel(target_model_name)
        
    except Exception as e:
        print(f"❌ 모델 목록 조회 실패: {e}")
        print("   기본값 'gemini-pro'로 시도합니다.")
        model = genai.GenerativeModel('gemini-pro')
else:
    model = None
    print("CRITICAL: GEMINI_API_KEY missing")

VALID_CATEGORIES = [
    "동화", "외국", "자연", "사회", "과학", "전통", "인물", "시", 
    "만화", "예술", "역사", "소설", "모음", "학부모", "지리"
]

# ==========================================
# 2. 서비스 함수
# ==========================================

async def get_book_description(isbn: str) -> str:
    if not ALADIN_TTB_KEY:
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
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "item" in data and len(data["item"]) > 0:
                        return data["item"][0].get("description", "")
        return None
    except Exception as e:
        print(f"   [API Error] {e}")
        return None

async def categorize_book_with_content(title, author, publisher, description):
    if not model:
        return "동화"
    
    # 상세 로그
    print(f"\n   [AI] 제목: {title}")
    if description:
        desc_preview = description[:100].replace('\n', ' ')
        print(f"   [AI] 책 소개: {desc_preview}...")
    else:
        print("   [AI] 책 소개 없음")

    parsed_desc = description[:1000] if description else ""
    
    prompt = f"""당신은 어린이 도서 전문 사서입니다. 다음 도서를 정확한 카테고리로 분류해주세요.

## 도서 정보
제목: {title}
저자: {author}
출판사: {publisher}
책 소개: {parsed_desc}

## 카테고리 정의
- **동화**: 창작 이야기, 전래동화, 우화, 픽션 스토리
- **외국**: 외국 작가의 번역서, 외국 문화 소개
- **자연**: 동물, 식물, 생태, 환경, 공룡 (예: 곤충 도감)
- **과학**: 과학 원리, 실험, 기술, 우주, 발명 (예: Why?)
- **역사**: 한국사, 세계사, 역사적 사건 (예: 한국사 편지)
- **전통**: 한국 전통문화, 민속놀이
- **인물**: 위인전, 인물 이야기
- **사회**: 사회 문제, 직업, 경제, 법, 정치
- **지리**: 지도, 세계 여러 나라
- **예술**: 미술, 음악, 공연
- **시**: 동시, 시집
- **만화**: 학습만화가 아닌 순수 만화
- **소설**: 장편 소설
- **모음**: 모음집
- **학부모**: 자녀 교육

## 중요 지침
- 단순히 '어린이 책'이라고 해서 '동화'로 분류하지 마세요.
- **논픽션**인 경우 주제에 맞게(과학, 자연, 역사 등) 분류하세요.
- 결과는 카테고리명 단어 하나만 출력하세요.

분류 결과 (카테고리명만):"""
    
    import traceback
    import time
    
    max_retries = 5
    retry_delay = 30
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            raw_res = response.text.strip()
            print(f"   [AI] Gemini Raw 응답: '{raw_res}'")
            
            category = raw_res.replace("'", "").replace('"', "").replace(".", "").split("\n")[0].strip()
            
            if category in VALID_CATEGORIES:
                return category
                
            for valid_cat in VALID_CATEGORIES:
                if valid_cat.lower() == category.lower():
                    return valid_cat
                    
            print(f"   [AI] ⚠️ 유효하지 않은 응답 -> 기본값 '동화' 사용")
            return "동화"
            
        except Exception as e:
            error_str = str(e)
            if "ResourceExhausted" in error_str or "429" in error_str:
                print(f"   [AI] ⏳ Quota 초과 (429). {retry_delay}초 대기 후 재시도 ({attempt+1}/{max_retries})...")
                await asyncio.sleep(retry_delay)
                # 대기 시간 점진적 증가
                retry_delay += 10
                continue
            else:
                # 그 외 에러는 로그 남기고 기본값 반환 (스크립트 중단 X)
                print(f"   [AI] ❌ API 오류: {e}")
                # traceback.print_exc()
                return "동화"
    
    print("   [AI] ❌ 최대 재시도 횟수 초과. 기본값 '동화' 반환")
    return "동화"

# ==========================================
# 3. 메인 로직
# ==========================================

async def run():
    # 윈도우 인코딩 문제 해결
    if sys.platform.startswith('win'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass
        
    print("=" * 80)
    print("겨울방학2026 도서 일괄 재분류 (Fully Standalone + Retry)")
    print("=" * 80)
    
    # 도서 조회
    result = supabase.table('childbook_items').select('id,title,category,author,publisher,isbn').eq('curation_tag', '겨울방학2026').execute()
    
    if not result.data:
        print("❌ 도서 없음")
        return

    books = result.data
    # 이미 로직이 개선되었으므로 전체 대상 처리.
    # 중단된 지점부터 하려면 DB에서 category가 '동화'인 것만 다시 하거나 할 수 있지만,
    # 일단은 전체를 다시 훑으면서 업데이트 (변경 없음이 뜰 것임)
    
    print(f"\n📚 총 {len(books)}권 처리 시작\n")
    
    for i, book in enumerate(books, 1):
        print(f"--------------------------------------------------")
        print(f"[{i}/{len(books)}] {book['title']}")
        # print(f"  현재: {book.get('category')}")
        
        # 1. 책 소개 조회 (필요시)
        description = None
        if book.get('isbn'):
            # 효율성을 위해 description이 비어있을 때만 가져오기 로직 추가 가능하지만
            # 아까 API 호출 문제는 없었으므로 유지 (단, 알라딘 API도 제한이 있을 수 있음)
            description = await get_book_description(book.get('isbn'))
            # description 로직은 간단히 유지
        
        # 2. 분류 (여기서 재시도 로직 수행됨)
        # 함수를 async로 변경해야 await 사용 가능. 
        # 위에서 await asyncio.sleep()을 썼으므로 함수 정의도 async로 바꿔야 함!
        new_category = await categorize_book_with_content(
            book['title'], 
            book.get('author'), 
            book.get('publisher'), 
            description
        )
        
        print(f"  ➡️ 분류 결과: {new_category}")
        
        # 3. DB 저장
        if new_category != book.get('category'):
            try:
                supabase.table('childbook_items').update({'category': new_category}).eq('id', book['id']).execute()
                print(f"  💾 DB 업데이트 완료 ({book.get('category')} -> {new_category})")
            except Exception as e:
                print(f"  ❌ DB 업데이트 실패: {e}")
        else:
            print("  ℹ️ 변경 없음")
            
        # 속도 조절: 무료 티어 안전 모드 (분당 15 requests = 4초, 여유있게 60초)
        print("  (대기 60초...)")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run())
