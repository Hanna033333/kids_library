"""
연령 교정 정합성 및 7-Book Rule 만족 여부 검증 스크립트
- 1. 청구기호와 연령대 간 남아있는 불일치 도서 통계 점검
- 2. 큐레이션 태그별 도서 개수를 카운트하여 7-Book Rule(테마당 7권 이상) 준수 여부 검사
"""
import os
import sys

# 백엔드 절대 경로 추가
sys.path.append('/Users/1004823/Desktop/kids_library/backend')

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv(dotenv_path="/Users/1004823/Desktop/kids_library/backend/.env", override=True)

from core.database import supabase
from core.taxonomy import VALID_TAXONOMY

def run_verification():
    print("=" * 60)
    print("📊 [검증] 도서 연령대 및 큐레이션 7-Book Rule 정합성 검사")
    print("=" * 60)
    
    # DB에서 데이터 로드
    try:
        res = supabase.table("childbook_items").select("id, title, pangyo_callno, age, curation_tag").execute()
        books = res.data
        print(f"로드 완료: 총 {len(books)}권의 도서 정보\n")
    except Exception as e:
        print(f"❌ DB 조회 실패: {e}")
        return

    # 1. 청구기호 vs 연령대 정합성 통계
    total_mismatches = 0
    mismatches = []
    
    older_ages = ['9세부터', '11세부터', '13세부터', '16세부터']
    younger_ages = ['0세부터', '3세부터', '5세부터']
    
    for b in books:
        callno = (b.get("pangyo_callno") or "").strip()
        age = (b.get("age") or "").strip()
        title = b.get("title") or ""
        
        if not callno or not age:
            continue
            
        prefix = callno[0]
        
        is_mismatch = False
        if prefix == '유' and any(oa in age for oa in older_ages):
            is_mismatch = True
        elif prefix == '아' and any(ya in age for ya in younger_ages):
            is_mismatch = True
            
        if is_mismatch:
            total_mismatches += 1
            mismatches.append(b)
            
    print(f"📌 [정합성 결과] 불일치 의심 도서 수: {total_mismatches}권")
    if total_mismatches > 0:
        print("⚠️ 남아있는 불일치 도서 예시 (상위 10권):")
        for idx, m in enumerate(mismatches[:10], 1):
            print(f"  {idx}. ID: {m['id']} | {m['title']}")
            print(f"     - 청구기호: {m['pangyo_callno']} | 연령대: {m['age']}")
    else:
        print("✅ 청구기호와 연령대 간의 모순(불일치)이 완전히 해결되었습니다!")
    print()

    # 2. 7-Book Rule 검사
    print("📌 [7-Book Rule 결과] 큐레이션 테마별 도서 개수 감사:")
    
    # 큐레이션별 도서 카운트
    curation_counts = {}
    
    for b in books:
        curation_tags = b.get("curation_tag") or ""
        # 콤마로 연결된 큐레이션 태그 파싱 (첫 번째 태그 정밀 매칭 기준)
        tags_list = [t.strip() for t in curation_tags.split(",") if t.strip()]
        if not tags_list:
            continue
            
        # 첫 번째 태그만 기준으로 카운트 (UX 정책 반영)
        first_tag = tags_list[0]
        # 샵(#) 기호가 있으면 떼어냄
        clean_tag = first_tag.replace("#", "")
        curation_counts[clean_tag] = curation_counts.get(clean_tag, 0) + 1
        
    # VALID_TAXONOMY 기준 검사
    violations_count = 0
    for taxonomy in VALID_TAXONOMY:
        tag = taxonomy["tag"]
        count = curation_counts.get(tag, 0)
        
        if count < 7:
            print(f"  ❌ 위반: 테마 '{tag}' -> 현재 {count}권 (7권 미만)")
            violations_count += 1
        else:
            # 정상 출력 (간략화)
            pass
            
    if violations_count > 0:
        print(f"\n⚠️ 경고: 총 {violations_count}개의 큐레이션 테마가 '7-Book Rule'을 위반하고 있습니다.")
        print("  - 데이터 정제 후 도서 수량이 부족한 주제가 존재하므로, 희소 태그 동적 분배 마이그레이션이 정상인지 확인 필요합니다.")
    else:
        print("✅ 모든 활성 큐레이션 테마가 '7-Book Rule'(최소 7권 이상)을 통과했습니다!")
        
    print("\n" + "=" * 60)
    print("검증 완료")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
