---
name: AI_Book_Categorization
description: 신규 도서 추가 시 AI(Gemini)와 알라딘 API를 활용하여 도서 카테고리를 자동으로 분류하는 스킬
---

# AI 도서 카테고리 자동 분류

신규 도서를 데이터베이스에 추가할 때, 알라딘 API로 책 소개(Description)를 가져오고 Google Gemini AI를 사용하여 적절한 카테고리를 자동으로 부여하는 방법입니다.

## 📁 위치
- **스킬 경로**: `.agent/skills/development/AI_Book_Categorization`
- **예제 코드**: `.agent/skills/development/AI_Book_Categorization/examples`

## 🛠️ 사전 요구사항 (Prerequisites)
1. **Google Gemini API Key** (Tier 1 권장, `.env`에 `GEMINI_API_KEY` 설정)
2. **Aladin TTB Key** (`.env`에 `ALADIN_TTB_KEY` 설정)
3. **Supabase Client** (`supabase_client` 모듈 사용 권장)

## ⚠️ 핵심 주의사항 (Troubleshooting & Best Practices)

이번 겨울방학 도서 40권 재분류 과정에서 얻은 **중요한 교훈**들입니다.

### 1. 프롬프트 엔지니어링 (정확도 향상)
단순히 "분류해줘"라고 하면 모든 책을 '동화'로 분류하는 경향이 있습니다.
**반드시 상세한 카테고리 정의와 예시를 프롬프트에 포함해야 합니다.**

```python
# ✅ 좋은 프롬프트 예시
prompt = """
## 카테고리 정의 (반드시 이 중 하나로 분류)
- **동화**: 창작 이야기, 전래동화, 우화 (예: 아기돼지 삼형제)
- **과학**: 과학 원리, 실험, 우주, 발명 (예: Why? 시리즈)
- **역사**: 한국사, 세계사 (예: 한국사 편지)
... (모든 카테고리 정의 포함)

## 중요 지침
1. 제목과 책 소개를 모두 고려하여 가장 적합한 하나를 선택하세요.
2. 논픽션(지식/정보)은 주제에 맞게 과학/역사/사회 등으로 분류하세요.
"""
```

### 2. API Rate Limit (429 에러) 해결
Gemini Tier 1 유료 플랜이라도 **RPM(분당 요청 수) 제한**이 있습니다.
반복 작업 시 **최소 10초 이상의 딜레이**를 주어야 429 에러를 피할 수 있습니다.

```python
# ✅ 안전한 반복 실행
for book in books:
    await categorize_book(...)
    await asyncio.sleep(10)  # 10초 대기 (분당 6회 요청)
```

### 3. 모델 선택 (Dynamic Model Selection)
특정 모델(`gemini-1.5-flash`)이 지역/상황에 따라 404 에러가 날 수 있습니다. 동적으로 모델을 찾는 로직을 권장합니다.

```python
# ✅ 동적 모델 탐색
available_models = [m.name for m in genai.list_models()]
target_model = next((m for m in available_models if 'gemini-2.0-flash' in m), 'models/gemini-1.5-flash')
```

### 4. 환경 변수 및 DB 업데이트
스크립트 실행 위치에 따라 `.env` 파일 경로가 달라질 수 있습니다.
가급적 검증된 `supabase_client` 모듈을 import하여 사용하는 것이 안전합니다.
자체적으로 `.env`를 파싱할 경우 경로 문제로 API 키가 로드되지 않을 수 있습니다.

## 🚀 사용 예시

### 단일 도서 분류 함수 (Wrapper)

```python
async def categorize_new_book(title, isbn):
    # 1. 알라딘 API로 Description 조회
    desc = await get_description(isbn)
    
    # 2. Gemini API로 카테고리 분류
    category = await categorize_with_ai(title, desc)
    
    return category, desc
```

자세한 구현 코드는 `examples/category_helper.py`를 참고하세요.
