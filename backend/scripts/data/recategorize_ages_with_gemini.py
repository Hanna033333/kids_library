"""
도서 연령대(Age) 정밀 재분류 스크립트 (Hybrid: Rule-based + Gemini AI)
- 1단계: 알라딘 TTB API를 통해 책의 description과 categoryName 수집
- 2단계: categoryName에 명시된 명확한 학년/연령대는 규칙 기반으로 자동 매핑 (1차 필터)
- 3단계: 카테고리가 모호하거나 (예: 초등 전학년), 정밀 판단이 필요한 그림책은 Gemini AI가 줄거리와 카테고리를 종합해 판단 (2단계 정밀 심사)
- 4단계: 기존 설정 연령과 다를 경우 Supabase DB 업데이트
"""
import os
import sys
import re
import asyncio
import aiohttp
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# backend 절대 경로 추가
sys.path.append('/Users/1004823/Desktop/kids_library/backend')

# 환경 변수 로드
load_dotenv(dotenv_path="/Users/1004823/Desktop/kids_library/backend/.env", override=True)

from core.database import supabase
from core.config import GEMINI_API_KEY, ALADIN_TTB_KEY

# Gemini 설정
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    target_model_name = 'gemini-2.5-flash'
    try:
        model_names = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        preferred = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-3.5-flash', 'gemini-pro-latest']
        found = False
        for pref in preferred:
            matched = [name for name in model_names if pref in name]
            if matched:
                target_model_name = matched[0]
                found = True
                break
        if not found and model_names:
            target_model_name = model_names[0]
    except Exception as e:
        print(f"⚠️ 모델 목록 조회 중 오류 발생: {e}. 기본값 'gemini-2.5-flash' 사용.")
    model = genai.GenerativeModel(target_model_name)
    print(f"🤖 Gemini 모델 설정 완료: {target_model_name}")
else:
    model = None
    print("❌ 경고: GEMINI_API_KEY가 존재하지 않습니다. AI 분류는 스킵됩니다.")

# 허용되는 연령 스키마
VALID_AGES = ['0세부터', '3세부터', '5세부터', '7세부터', '9세부터', '11세부터', '13세부터', '16세부터']

# 알라딘 카테고리 정보 조회 함수
async def fetch_aladin_meta(isbn: str) -> dict:
    if not ALADIN_TTB_KEY or not isbn:
        return {"description": "", "categoryName": ""}
        
    url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        "ttbkey": ALADIN_TTB_KEY,
        "itemIdType": "ISBN13" if len(isbn.strip()) == 13 else "ISBN",
        "ItemId": isbn.strip(),
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
                        item = data["item"][0]
                        return {
                            "description": item.get("description", ""),
                            "categoryName": item.get("categoryName", "")
                        }
        return {"description": "", "categoryName": ""}
    except Exception as e:
        print(f"   [알라딘 API 에러] ISBN {isbn}: {e}")
        return {"description": "", "categoryName": ""}

# 1차 규칙 기반 매핑 함수
def rule_based_classify(category_name: str, title: str) -> str:
    """
    알라딘 카테고리명 텍스트 파싱을 통한 1차 매핑
    반환값이 None이면 AI 정밀 판단 대상으로 분류
    """
    if not category_name:
        return None
        
    # 국내도서 > 어린이 > 초등5-6학년 > ...
    if '초등5-6학년' in category_name:
        return '11세부터'
    elif '초등3-4학년' in category_name:
        return '9세부터'
    elif '초등1-2학년' in category_name:
        return '7세부터'
        
    # 국내도서 > 유아 > 0-3세 > ...
    if '0-3세' in category_name or '영아' in category_name:
        # 영아용 그림책은 보통 0세 혹은 3세부터
        return '3세부터'
        
    # 국내도서 > 유아 > 4-6세 > ...
    # 단, 그림책의 경우 '우리 아빠는 위대한 해적'처럼 4-6세로 대분류되어 있으나 실제 주제가 깊은 경우(상실, 죽음 등)가 있음.
    # 따라서 유아 도서 중 특정 민감 키워드가 제목에 포함된 경우는 룰 베이스 분류를 우회하여 AI 심사를 받도록 함.
    sensitive_keywords = ['죽음', '상실', '전쟁', '이별', '탄광', '해적', '역사', '위인', '눈물', '불안']
    if any(kw in title for kw in sensitive_keywords):
        return None  # AI 심사 유도
        
    if '4-6세' in category_name or '7세' in category_name or '5-7세' in category_name or '유아 그림책' in category_name:
        return '5세부터'
        
    if '청소년' in category_name:
        return '13세부터'
        
    return None  # 모호한 카테고리는 AI 판단 위임

# 2차 Gemini AI 정밀 재분류 함수
async def ai_classify(title: str, author: str, publisher: str, category_name: str, description: str) -> str:
    if not model:
        return None
        
    desc_clean = description[:800].replace('\n', ' ') if description else "줄거리 정보 없음"
    cat_clean = category_name if category_name else "카테고리 정보 없음"
    
    prompt = f"""당신은 어린이 도서 전문 사서이자 아동 발달/독서 지도 전문가입니다.
제공된 도서 정보, 알라딘 장르 카테고리, 그리고 줄거리를 종합적으로 분석하여 이 책을 읽기에 가장 적절한 '권장 시작 연령대'를 선택해주세요.

도서 정보:
- 제목: {title}
- 저자: {author}
- 출판사: {publisher}
- 알라딘 장르 카테고리: {cat_clean} (이 정보에 구체적인 학년이나 연령대가 있다면 매우 유력한 단서가 됩니다.)
- 책 소개/줄거리: {desc_clean}

선택 가능한 연령대 목록:
['0세부터', '3세부터', '5세부터', '7세부터', '9세부터', '11세부터', '13세부터', '16세부터']

결정 가이드:
1. 책의 어휘 난이도, 글줄의 양(그림 위주인지 글밥이 많은지), 그리고 다루는 주제의 깊이를 최우선으로 하세요.
   - 예: 죽음, 전쟁, 탄광 사고, 심오한 철학적 우화 등 무거운 감정이나 사회적 주제를 다루는 그림책은 설령 그림책이더라도 '7세부터' 혹은 '9세부터' 이상으로 분류해야 합니다.
2. 알라딘 장르 카테고리에 '초등1-2학년'이 명시되어 있다면 보통 '7세부터'가 적합하고, '초등3-4학년'은 '9세부터', '초등5-6학년'은 '11세부터'가 적합합니다.
3. 결과는 반드시 목록에 명시된 문자열 하나로만 정확히 출력하세요. 설명이나 서론, 부연설명은 절대 추가하지 마세요. (예: '7세부터')

분류 결과:"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(model.generate_content, prompt)
            raw_res = response.text.strip()
            
            # 특수문자 제거 및 정제
            clean_res = raw_res.replace("'", "").replace('"', "").replace(".", "").strip()
            
            if clean_res in VALID_AGES:
                return clean_res
                
            # 부분 일치 검색
            for age in VALID_AGES:
                if age in clean_res:
                    return age
                    
            print(f"   [Gemini] 유효하지 않은 응답 형식: '{raw_res}' -> 재시도 중 ({attempt+1}/{max_retries})")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"   [Gemini API 에러] {e} -> 재시도 중 ({attempt+1}/{max_retries})")
            await asyncio.sleep(2)
            
    return None

async def main():
    print("=" * 60)
    print("🚀 도서 연령대(Age) 하이브리드 정밀 재분류 스크립트 시작")
    print("=" * 60)
    
    # 1. 대상 도서 로드
    # - 불일치 의심 조건:
    #   A) pangyo_callno가 '유'로 시작하는데 age가 8세 이상 (9세부터, 11세부터, 13세부터, 16세부터)
    #   B) pangyo_callno가 '아'로 시작하는데 age가 5세 이하 (0세부터, 3세부터, 5세부터)
    #   C) age가 비어있거나 NULL인 도서
    try:
        res = supabase.table("childbook_items").select("id, title, author, publisher, pangyo_callno, age, isbn").execute()
        all_books = res.data
        print(f"DB에서 총 {len(all_books)}권의 도서를 로드했습니다.")
    except Exception as e:
        print(f"❌ DB 조회 실패: {e}")
        return
        
    target_books = []
    older_ages = ['9세부터', '11세부터', '13세부터', '16세부터']
    younger_ages = ['0세부터', '3세부터', '5세부터']
    
    for b in all_books:
        callno = (b.get("pangyo_callno") or "").strip()
        age = (b.get("age") or "").strip()
        
        if not callno:
            # 청구기호가 없지만 age가 비어있는 경우 대상에 포함
            if not age:
                target_books.append(b)
            continue
            
        prefix = callno[0]
        
        # Case A: '유'인데 8세 이상인 경우
        if prefix == '유' and any(oa in age for oa in older_ages):
            target_books.append(b)
        # Case B: '아'인데 5세 이하인 경우
        elif prefix == '아' and any(ya in age for ya in younger_ages):
            target_books.append(b)
        # Case C: age가 아예 없는 경우
        elif not age:
            target_books.append(b)
            
    print(f"🎯 정밀 교정 대상 도서: 총 {len(target_books)}권\n")
    
    if not target_books:
        print("교정 대상 도서가 없습니다. 작업을 종료합니다.")
        return
        
    success_count = 0
    updated_count = 0
    
    for idx, book in enumerate(target_books, 1):
        book_id = book['id']
        title = book['title']
        author = book.get('author') or ""
        publisher = book.get('publisher') or ""
        isbn = book.get('isbn') or ""
        old_age = book.get('age') or "NULL"
        
        print(f"[{idx}/{len(target_books)}] ID: {book_id} | 제목: {title} (기존 연령: {old_age})")
        
        # 1. 알라딘 메타데이터 조회
        meta = await fetch_aladin_meta(isbn)
        cat_name = meta["categoryName"]
        desc = meta["description"]
        
        if cat_name:
            print(f"   - [알라딘 카테고리] {cat_name}")
        else:
            print("   - ⚠️ 알라딘 카테고리 조회 실패/누락")
            
        # 2. 1단계: 규칙 기반 파싱 시도
        new_age = rule_based_classify(cat_name, title)
        classify_method = "Rule-based"
        
        # 3. 2단계: 규칙 기반 파싱 실패 시 AI 분류 위임
        if not new_age:
            if model:
                print("   - 🤖 AI 정밀 심사 진행 중...")
                new_age = await ai_classify(title, author, publisher, cat_name, desc)
                classify_method = "Gemini AI"
            else:
                new_age = None
                
        # 4. 연령 결정 및 업데이트 반영
        if new_age and new_age in VALID_AGES:
            print(f"   - ➡️ 최종 결정 연령: {new_age} (방법: {classify_method})")
            
            if new_age != old_age:
                try:
                    supabase.table("childbook_items").update({"age": new_age}).eq("id", book_id).execute()
                    print(f"   - 💾 DB 업데이트 성공: {old_age} -> {new_age}")
                    updated_count += 1
                except Exception as e:
                    print(f"   - ❌ DB 업데이트 실패: {e}")
            else:
                print("   - ℹ️ 변경 사항 없음 (AI 판정 결과 기존과 동일)")
                
            success_count += 1
        else:
            print("   - ❌ 연령 분류 실패 (정보 부족 또는 AI 판단 보류)")
            
        print("-" * 50)
        
        # API 과부하 및 할당량 방지를 위한 딜레이 (AI 호출 시 4초, 일반 룰베이스 시 0.5초)
        delay = 4 if classify_method == "Gemini AI" else 0.5
        await asyncio.sleep(delay)
        
    print("\n" + "=" * 60)
    print("🎉 재분류 작업 완료!")
    print(f"- 총 대상: {len(target_books)}권")
    print(f"- 분류 성공: {success_count}권")
    print(f"- DB 업데이트: {updated_count}권")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
