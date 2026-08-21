#!/usr/bin/env python3
"""
어린이도서연구회 단독 태그 도서 51권 AI 태깅 및 줄거리 보강 스크립트

1. childbook_items에서 curation_tag == '어린이도서연구회'인 도서 조회
2. description이 없으면 알라딘 TTB API로 줄거리 조회/보강
3. Gemini AI를 통해 도서의 핵심 주제 태그(1~3개) 생성
4. curation_tag를 '#태그1,#태그2,어린이도서연구회' 형태로 병합 업데이트
"""

import sys
import os
import json
import time
from pathlib import Path
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# 백엔드 루트 및 .env 로드
backend_dir = Path("/Users/1004823/Desktop/kids_library/backend")
sys.path.append(str(backend_dir))
load_dotenv(backend_dir / ".env")

from core.database import supabase

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALADIN_KEY = os.getenv("ALADIN_TTB_KEY", "ttbrkdgkssk011716001")
MODEL_NAME = "gemini-2.5-flash"
ALADIN_API = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"

# 79개 표준 태그 목록
ALL_TAGS = [
    # 감성/정서 발달
    "잠자리", "감정조절", "자존감", "배려", "생명존중", "가족사랑", "적응", "상실",
    "용기", "우정", "정직", "나눔", "분노조절", "슬픔", "질투", "두려움",
    "끈기", "위로", "행복", "용서",
    # 사회/관계
    "사회성", "다양성", "규칙", "다문화", "진로", "경제", "의사소통", "평화",
    "장애", "양성평등", "이웃", "미디어",
    # 과학/자연
    "인체", "자연관찰", "환경보호", "과학원리", "계절", "곤충", "우주", "공룡",
    "바다", "식물", "날씨", "코딩", "인공지능", "수학", "발명",
    # 문화/예술
    "우리문화", "역사이야기", "전래동화", "예술감성", "음악", "연극", "세계역사",
    "명화", "건축", "명절", "전통놀이", "한글", "글쓰기",
    # 이야기/장르
    "모험", "판타지", "유머", "추리", "상상력", "하늘", "요리", "패션",
    "탈것", "스포츠", "괴물", "미래도시", "신체활동", "자연재해", "생활습관",
    "인문지리", "동물도감", "미래상상"
]


def fetch_aladin_description(isbn: str) -> str:
    """알라딘 API를 통해 책 소개글을 가져옵니다."""
    if not isbn:
        return ""
    try:
        clean_isbn = isbn.replace("-", "").strip()
        params = {
            "ttbkey": ALADIN_KEY,
            "itemIdType": "ISBN13" if len(clean_isbn) == 13 else "ISBN",
            "ItemId": clean_isbn,
            "output": "js",
            "Version": "20131101",
            "OptResult": "description"
        }
        res = requests.get(ALADIN_API, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if "item" in data and len(data["item"]) > 0:
                desc = data["item"][0].get("description", "")
                return desc.strip()
    except Exception as e:
        print(f"  [알라딘 조회 실패] ISBN {isbn}: {e}")
    return ""


def main():
    print("🚀 어린이도서연구회 단독 도서 AI 태깅 시작...")
    
    # 1. 대상 도서 조회
    res = supabase.table("childbook_items")\
        .select("id, title, author, description, isbn, curation_tag")\
        .eq("curation_tag", "어린이도서연구회")\
        .execute()
    
    books = res.data or []
    print(f"총 대상 도서: {len(books)}권")
    
    if not books:
        print("태깅할 대상 도서가 없습니다.")
        return

    # 2. 알라딘 줄거리 보강
    print("\n📚 1단계: 줄거리(description) 보강 중...")
    for b in books:
        if not b.get("description") or len(b.get("description", "")) < 20:
            isbn = b.get("isbn")
            if isbn:
                desc = fetch_aladin_description(isbn)
                if desc:
                    b["description"] = desc
                    # DB에도 description 업데이트
                    try:
                        supabase.table("childbook_items").update({"description": desc}).eq("id", b["id"]).execute()
                        print(f"  ✓ [{b['id']}] {b['title']} 줄거리 보강 완료 ({len(desc)}자)")
                    except Exception as e:
                        print(f"  ✗ [{b['id']}] DB 줄거리 업데이트 실패: {e}")
                time.sleep(0.1)

    # 3. Gemini AI 태깅 배치 실행
    print("\n🤖 2단계: Gemini AI 태그 생성 및 DB 반영 중...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
    
    BATCH_SIZE = 7
    total_updated = 0
    
    tag_list_str = ", ".join(ALL_TAGS)
    
    for i in range(0, len(books), BATCH_SIZE):
        batch = books[i:i+BATCH_SIZE]
        print(f"\n--- 배치 처리 중 ({i+1}~{min(i+BATCH_SIZE, len(books))}/{len(books)}) ---")
        
        books_str = ""
        for idx, b in enumerate(batch):
            desc = (b.get('description') or '줄거리 정보 없음')[:400]
            books_str += f"[{idx+1}] ID: {b['id']}, 제목: {b['title']}, 작가: {b.get('author', '미상')}\n"
            books_str += f"내용: {desc}\n\n"
            
        prompt = f"""당신은 20년 경력의 베테랑 어린이 도서 사서이자 육아 전문가입니다.
제공된 {len(batch)}권의 도서를 분석하여, 도서의 핵심 주제와 메시지에 가장 부합하는 태그를 1~3개 선택해주세요.

[사용 가능한 태그 목록 (79개)]
{tag_list_str}

[규칙]
1. 각 도서에 1~3개 태그만 선택하세요.
2. 반드시 위 목록에 있는 태그만 사용하세요.
3. 태그 앞에 '#'을 붙이지 마세요.
4. confidence_score는 85~98 사이 정수로 평가하세요.

[출력 형식: JSON 배열]
[
  {{
    "id": 123,
    "tags": ["가족사랑", "배려"],
    "confidence_score": 95
  }}
]

[분석 대상 도서]
{books_str}"""

        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            raw_text = response.text.strip()
            results = json.loads(raw_text)
            
            for res_item in results:
                book_id = res_item.get("id")
                ai_tags = res_item.get("tags", [])
                conf = res_item.get("confidence_score", 90)
                
                # 유효한 태그만 필터링
                valid_tags = [f"#{t.lstrip('#')}" for t in ai_tags if t.lstrip('#') in ALL_TAGS]
                if not valid_tags:
                    valid_tags = ["#감성", "#성장"]
                    
                # '어린이도서연구회' 태그 보존하여 병합
                final_tag_str = f"{','.join(valid_tags)},어린이도서연구회"
                
                try:
                    supabase.table("childbook_items").update({
                        "curation_tag": final_tag_str,
                        "confidence_score": conf
                    }).eq("id", book_id).execute()
                    
                    matched_title = next((b['title'] for b in batch if b['id'] == book_id), "알 수 없음")
                    print(f"  ✓ [{book_id}] {matched_title} ➔ {final_tag_str}")
                    total_updated += 1
                except Exception as e:
                    print(f"  ✗ [{book_id}] DB 업데이트 실패: {e}")
                    
        except Exception as e:
            print(f"  ✗ 배치 AI 호출 실패: {e}")
            
        time.sleep(1.0)

    print(f"\n🎉 완료! 총 {total_updated}권의 도서에 AI 태그가 성공적으로 병합되었습니다.")

if __name__ == "__main__":
    main()
