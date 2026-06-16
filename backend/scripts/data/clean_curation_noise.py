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
from rule_based_audit import NOISE_PATTERNS

def clean_curation_noise():
    print("🧹 [7-Book Rule 정합성 정제] 오매칭 노이즈 정제 작업 시작...")
    
    try:
        response = supabase.table("childbook_items").select("id, title, description, keywords, curation_note, curation_tag").execute()
        books = response.data
        print(f"Loaded {len(books)} books from database.")
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return

    # 각 테마별 도서 개수 사전 조사 (정제 전)
    theme_counts_before = {}
    for b in books:
        tags = [t.strip() for t in (b.get("curation_tag") or "").split(",") if t.strip()]
        for tag in tags:
            theme_counts_before[tag] = theme_counts_before.get(tag, 0) + 1

    # 정제 후 예상되는 도서 태그들 및 테마별 개수 계산
    books_to_update = []
    theme_counts_after = theme_counts_before.copy()
    
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
        
        updated_tags = tags_list.copy()
        removed_tags = []
        
        for tag, rules in NOISE_PATTERNS.items():
            if tag in updated_tags:
                for keyword, patterns in rules:
                    if keyword in full_text:
                        for pat in patterns:
                            matches = re.findall(pat, full_text)
                            if matches:
                                # 오매칭으로 간주하고 해당 태그 제거
                                updated_tags.remove(tag)
                                removed_tags.append(tag)
                                break
                                
        if removed_tags:
            # 예상 개수 반영
            for tag in removed_tags:
                theme_counts_after[tag] = theme_counts_after.get(tag, 0) - 1
            
            books_to_update.append({
                "id": book_id,
                "title": title,
                "original_tags": curation_tags,
                "new_tags": ",".join(updated_tags),
                "removed_tags": removed_tags
            })

    # 안전장치(Safety Guard) 작동
    # 정제 이후 각 테마의 도서 수량이 7권 미만으로 떨어지는 테마가 있는지 검사
    below_limit_themes = {}
    for theme, count in theme_counts_after.items():
        # theme은 '#인체' 형식
        if count < 7:
            below_limit_themes[theme] = {
                "before": theme_counts_before.get(theme, 0),
                "after": count
            }
            
    if below_limit_themes:
        print("\n⚠️ [안전장치 작동] 정제 시 7-Book Rule(테마당 최소 7권)을 위반하는 큐레이션 테마가 감지되었습니다!")
        for theme, info in below_limit_themes.items():
            print(f"   - {theme}: 정제 전 {info['before']}권 -> 정제 후 {info['after']}권 (7권 미만)")
        
        print("\n❌ 7-Book Rule 정합성 유지를 위해 정제 일괄 업데이트를 중단(Abort)합니다.")
        print("💡 해결 방안: 위 큐레이션 테마들에 대해 도서관 소장 여부와 무관하게 7권 이상이 유지되도록 신규 도서 데이터를 먼저 추가하거나, 유사한 다른 도서로 채워주세요.")
        return

    # 안전성 통과 시 실제로 업데이트 적용
    print(f"\n✅ 안전장치 통과: 정제 후 모든 테마가 7-Book Rule(7권 이상)을 충족합니다.")
    print(f"업데이트 대상 도서 수: {len(books_to_update)}권")
    
    # --yes 인자가 있으면 자동 승인
    if "--yes" in sys.argv:
        confirm = 'yes'
    else:
        confirm = input("⚠️ 실제로 Supabase 데이터베이스에 업데이트를 반영하시겠습니까? (yes/no): ").strip().lower()
        
    if confirm != 'yes':
        print("❌ 사용자가 승인하지 않아 정제 작업을 취소합니다.")
        return

    print("🚀 DB 업데이트 시작...")
    success_count = 0
    for item in books_to_update:
        try:
            supabase.table("childbook_items").update({"curation_tag": item["new_tags"]}).eq("id", item["id"]).execute()
            success_count += 1
        except Exception as e:
            print(f"❌ [ID: {item['id']} - {item['title']}] 업데이트 실패: {e}")
            
    print(f"🎉 정제 완료! 총 {success_count}/{len(books_to_update)}권의 도서 오매칭 태그가 정제되었습니다.")

if __name__ == "__main__":
    clean_curation_noise()
