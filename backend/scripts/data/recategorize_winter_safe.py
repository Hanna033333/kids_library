"""
비용 안전 장치가 포함된 AI 카테고리 분류 스크립트

- 최대 처리 권수 제한
- 예상 비용 계산 및 경고
- 사용자 확인 프롬프트
"""
import os
import sys
import asyncio
import aiohttp
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# 안전 설정
# ==========================================
MAX_BOOKS_PER_RUN = 100  # 한 번에 최대 100권만 처리
COST_PER_BOOK_USD = 0.0002  # 책 1권당 약 $0.0002 (매우 보수적 추정)
DAILY_BUDGET_USD = 1.0  # 일일 예산 $1

# ==========================================
# 환경 변수 로드
# ==========================================
def load_env_manual():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    paths_to_check = [
        os.path.join(current_dir, ".env"),
        os.path.join(os.path.dirname(current_dir), ".env"),
    ]
    
    env_vars = {}
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"): continue
                        if "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip().strip("'").strip('"')
                break
            except: pass
    return env_vars

env = load_env_manual()
GEMINI_API_KEY = env.get("GEMINI_API_KEY")
ALADIN_TTB_KEY = env.get("ALADIN_TTB_KEY")
SUPABASE_URL = env.get("SUPABASE_URL")
SUPABASE_KEY = env.get("SUPABASE_KEY")

VALID_CATEGORIES = [
    "동화", "외국", "자연", "사회", "과학", "전통", "인물", "시", 
    "만화", "예술", "역사", "소설", "모음", "학부모", "지리"
]

# Supabase 초기화
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"CRITICAL: Supabase Init Failed: {e}")
    sys.exit(1)

# Gemini 초기화
model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        # 사용 가능한 모델 찾기
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        print(f"✅ 사용 가능한 모델: {available_models}")
        
        # 우선순위: gemini-2.0-flash-exp > gemini-1.5-flash > gemini-pro
        target_model = None
        for model_name in available_models:
            if 'gemini-2.0-flash' in model_name or 'gemini-1.5-flash' in model_name:
                target_model = model_name
                break
        
        if not target_model and available_models:
            target_model = available_models[0]  # 첫 번째 사용 가능한 모델
        
        if target_model:
            model = genai.GenerativeModel(target_model)
            print(f"✅ Gemini Model: {target_model}")
        else:
            print("❌ 사용 가능한 모델이 없습니다!")
    except Exception as e:
        print(f"❌ Gemini 초기화 실패: {e}")
        import traceback
        traceback.print_exc()

# ==========================================
# 핵심 함수
# ==========================================
async def get_book_description(isbn: str) -> str:
    if not ALADIN_TTB_KEY or not isbn:
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

async def categorize_book_gpt(title, author="", publisher="", description=""):
    if not model:
        print("  ⚠️ 모델 없음 -> 기본값")
        return "동화"
    
    parsed_desc = description[:1000] if description else ""
    
    prompt = f"""당신은 어린이 도서 전문 사서입니다. 다음 도서를 정확한 카테고리로 분류해주세요.

## 도서 정보
제목: {title}
저자: {author}
출판사: {publisher}
책 소개: {parsed_desc}

## 카테고리 정의 (반드시 이 중 하나로 분류)

- **동화**: 창작 이야기, 전래동화, 우화, 픽션 스토리 (예: 아기돼지 삼형제, 신데렐라)
- **외국**: 외국 작가의 번역서, 외국 문화 소개 (예: 해리포터, 샬롯의 거미줄)
- **자연**: 동물, 식물, 생태, 환경, 공룡 (예: 곤충 도감, 동물의 왕국)
- **과학**: 과학 원리, 실험, 기술, 우주, 발명 (예: Why? 시리즈, 과학 실험)
- **역사**: 한국사, 세계사, 역사적 사건 (예: 한국사 편지, 세계사 이야기)
- **전통**: 한국 전통문화, 민속놀이, 전통 의상/음식 (예: 탈춤, 한복 이야기)
- **인물**: 위인전, 인물 이야기 (예: 세종대왕, 아인슈타인)
- **사회**: 사회 문제, 직업, 경제, 법, 정치 (예: 직업 탐험, 경제 이야기)
- **지리**: 지도, 세계 여러 나라, 지형 (예: 세계 지도 그림책)
- **예술**: 미술, 음악, 공연 (예: 명화 이야기, 악기 소개)
- **시**: 동시, 시집 (예: 동시집, 시 모음)
- **만화**: 학습만화가 아닌 순수 만화 (예: 코믹 만화)
- **소설**: 장편 소설 (예: 어린이 장편소설)
- **모음**: 여러 이야기 모음집
- **학부모**: 자녀 교육서 (부모용)

## 중요 지침
1. **제목과 책 소개를 모두 고려**하여 가장 적합한 카테고리를 선택하세요
2. **논픽션(지식/정보 전달)**인 경우: 주제에 맞게 과학/자연/역사/사회 등으로 분류
3. **픽션(이야기)**인 경우: 동화/외국/소설 중 선택
4. **학습만화(Why? 시리즈 등)**는 '과학' 또는 해당 주제 카테고리로 분류
5. **결과는 카테고리명 단어 하나만** 출력하세요 (설명 없이)

분류 결과:"""

    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            print(f"  🤖 AI 응답: '{raw_text}'")
            
            result = raw_text.replace("'", "").replace('"', "").split("\n")[0]
            
            for vc in VALID_CATEGORIES:
                if vc == result or vc in result:
                    return vc
            
            print(f"  ⚠️ 유효하지 않은 응답 '{result}' -> 기본값")
            return "동화"

        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ API 에러 (시도 {attempt+1}/{max_retries}): {error_msg[:100]}")
            
            if "429" in error_msg or "ResourceExhausted" in error_msg:
                await asyncio.sleep(retry_delay)
                retry_delay += 5
                continue
            else:
                print(f"  ⚠️ 복구 불가능한 에러 -> 기본값")
                return "동화"
    
    print(f"  ⚠️ 최대 재시도 초과 -> 기본값")
    return "동화"

# ==========================================
# 메인 실행
# ==========================================
async def run():
    if sys.platform.startswith('win'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except: pass
        
    print("=" * 80)
    print("💰 비용 안전 모드: 겨울방학2026 도서 재분류")
    print("=" * 80)
    
    # 도서 조회
    result = supabase.table('childbook_items').select(
        'id,title,category,author,publisher,isbn'
    ).eq('curation_tag', '겨울방학2026').execute()
    
    if not result.data:
        print("❌ 도서 없음")
        return

    books = result.data
    total = len(books)
    
    # 안전 체크
    if total > MAX_BOOKS_PER_RUN:
        print(f"⚠️  경고: 총 {total}권이 발견되었습니다.")
        print(f"   안전을 위해 최대 {MAX_BOOKS_PER_RUN}권만 처리합니다.")
        books = books[:MAX_BOOKS_PER_RUN]
        total = MAX_BOOKS_PER_RUN
    
    estimated_cost = total * COST_PER_BOOK_USD
    
    print(f"\n📊 처리 정보:")
    print(f"   대상 도서: {total}권")
    print(f"   예상 비용: ${estimated_cost:.4f} (약 ₩{estimated_cost * 1300:.0f}원)")
    print(f"   일일 예산: ${DAILY_BUDGET_USD}")
    
    if estimated_cost > DAILY_BUDGET_USD:
        print(f"\n❌ 예상 비용(${estimated_cost:.2f})이 일일 예산(${DAILY_BUDGET_USD})을 초과합니다!")
        print(f"   MAX_BOOKS_PER_RUN을 조정하거나 여러 날에 나눠서 실행하세요.")
        return
    
    # 사용자 확인 (자동 실행 시 주석 처리)
    # confirm = input("\n계속 진행하시겠습니까? (y/N): ")
    # if confirm.lower() != 'y':
    #     print("취소되었습니다.")
    #     return
    
    print(f"\n🚀 처리 시작...\n")
    
    processed = 0
    for i, book in enumerate(books, 1):
        print(f"[{i}/{total}] {book['title']}")
        
        # 책 소개 조회
        description = None
        if book.get('isbn'):
            description = await get_book_description(book.get('isbn'))
        
        # 분류
        new_category = await categorize_book_gpt(
            book['title'], 
            book.get('author'), 
            book.get('publisher'), 
            description
        )
        
        print(f"  ➡️ {new_category}")
        
        # DB 저장
        if new_category != book.get('category'):
            try:
                supabase.table('childbook_items').update({
                    'category': new_category
                }).eq('id', book['id']).execute()
                print(f"  ✅ 업데이트 완료")
            except Exception as e:
                print(f"  ❌ DB 오류: {e}")
        
        processed += 1
        
        # 속도 조절 (Tier 1 RPM 한도 고려)
        await asyncio.sleep(10)  # 10초 대기 (분당 6 requests, 안전)
    
    print(f"\n{'=' * 80}")
    print(f"✅ 완료: {processed}권 처리")
    print(f"💰 실제 비용은 Google Cloud Console에서 확인하세요.")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    asyncio.run(run())
