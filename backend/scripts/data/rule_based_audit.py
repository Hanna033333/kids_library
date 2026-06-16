import sys
import os
import re
from pathlib import Path
from dotenv import load_dotenv

# backend/.env 파일을 명시적으로 로드
load_dotenv(dotenv_path="/Users/1004823/Desktop/kids_library/backend/.env", override=True)

# backend/scripts/data를 path에 추가하여 supabase_client 임포트 가능하게 설정
backend_scripts_data = Path(__file__).parent
sys.path.append(str(backend_scripts_data))

from supabase_client import supabase

# 오매칭 의심 규칙 정의
# {태그: [(매칭 키워드, 오매칭 유발 패턴들)]}
NOISE_PATTERNS = {
    "#인체": [
        ("피", [r"[가-힣]*피우[가-힣]*", r"[가-힣]*피어[가-힣]*", r"[가-힣]*피해[가-힣]*", r"피자", r"피리", r"피아노", r"커피", r"스피드", r"해피", r"카피", r"레시피"])
    ],
    "#탈것": [
        ("차", [r"차가운", r"차분한", r"차례", r"차이", r"차오르", r"점차", r"마차", r"마주차", r"차츰", r"교차", r"2차", r"1차", r"3차", r"다차원", r"식차", r"마시는 차", r"녹차", r"홍차", r"찻집"])
    ],
    "#진로": [
        ("일", [r"일생", r"일요일", r"일찍", r"일부", r"일기", r"일어나", r"일곱", r"일단", r"일이", r"일들", r"일만", r"일일", r"매일", r"동일", r"통일", r"주일", r"과일", r"독일", r"제일", r"일으키"])
    ],
    "#의사소통": [
        ("이해", [r"이해하기 쉽게 설명", r"쉽게 이해하도록", r"도와줍니다"])
    ],
    "#장애": [
        ("이해", [r"이해하기 쉽게 설명", r"쉽게 이해하도록"])
    ],
    "#명화": [
        ("그림", [r"그림책", r"그림을", r"그림이", r"그림으로"]) # 단순 그림책 명칭 노이즈
    ],
    "#우리문화": [
        ("우리", [r"우리 엄마", r"우리 아빠", r"우리 가족", r"우리 집", r"우리 동네", r"우리 강아지", r"우리 아이", r"우리가", r"우리 모두", r"우리 함께"])
    ]
}

def audit_books():
    print("🔍 [7-Book Rule 정합성 감사] 오매칭 노이즈 감사 시작...")
    
    try:
        response = supabase.table("childbook_items").select("id, title, description, keywords, curation_note, curation_tag").execute()
        books = response.data
        print(f"Loaded {len(books)} books from database.")
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return []

    audit_results = []
    
    for b in books:
        book_id = b.get("id")
        title = b.get("title") or ""
        desc = b.get("description") or ""
        keyw = b.get("keywords") or ""
        note = b.get("curation_note") or ""
        curation_tags = b.get("curation_tag") or ""
        
        tags_list = [t.strip() for t in curation_tags.split(",") if t.strip()]
        if not tags_list:
            continue
            
        full_text = f"{title} {desc} {keyw} {note}"
        
        detected_noises = []
        
        for tag, rules in NOISE_PATTERNS.items():
            if tag in tags_list:
                for keyword, patterns in rules:
                    # 키워드가 본문에 들어있는지 확인
                    if keyword in full_text:
                        # 오매칭 패턴 중 하나라도 매칭되는지 확인
                        for pat in patterns:
                            matches = re.findall(pat, full_text)
                            if matches:
                                # 예외적인 오매칭으로 간주될 만한 패턴이 감지됨
                                # 단, 오매칭 키워드가 들어간 곳이 전부 이 노이즈 패턴들로만 설명되는지 검증
                                # 간단히 감지 리스트에 추가
                                detected_noises.append({
                                    "tag": tag,
                                    "keyword": keyword,
                                    "matched_pattern": pat,
                                    "snippets": matches
                                })
                                break # 이 태그에 대해 감지 완료
                                
        if detected_noises:
            audit_results.append({
                "id": book_id,
                "title": title,
                "tags": tags_list,
                "noises": detected_noises
            })
            
    print(f"\n📢 감사 완료: 총 {len(audit_results)}권의 도서에서 오매칭 의심 사례가 발견되었습니다.")
    for res in audit_results[:10]: # 상위 10개만 출력
        print(f"📖 ID: {res['id']} | 제목: {res['title']}")
        print(f"   현재 태그: {res['tags']}")
        for noise in res["noises"]:
            print(f"   ⚠️ 의심 태그: {noise['tag']} (키워드 '{noise['keyword']}'가 패턴 '{noise['matched_pattern']}'에 매칭됨: {noise['snippets']})")
        print("-" * 50)
        
    return audit_results

if __name__ == "__main__":
    audit_books()
