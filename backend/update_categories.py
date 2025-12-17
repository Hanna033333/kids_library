import csv
import os
from supabase_client import supabase

def update_categories():
    filename = "category_list.csv"
    if not os.path.exists(filename):
        print("❌ category_list.csv 파일이 없습니다.")
        return

    mapping = []
    # 인코딩 확인 및 읽기
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    for enc in encodings:
        try:
            with open(filename, "r", encoding=enc) as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        old = row[0].strip()
                        new = row[1].strip()
                        if old and new:
                            mapping.append((old, new))
            print(f"✅ CSV 읽기 성공 ({enc})")
            break
        except:
            continue
            
    if not mapping:
        print("❌ 매핑 정보를 읽을 수 없습니다.")
        return
        
    print(f"🔄 총 {len(mapping)}개의 카테고리 매핑을 적용합니다.")
    
    total_updated = 0
    for old, new in mapping:
        if old == new:
            continue
            
        try:
            # 해당 카테고리를 가진 책 개수 확인 (선택사항이지만 로그용으로 좋음)
            # count = supabase.table("childbook_items").select("id", count="exact").eq("category", old).execute()
            # print(f"  - {old} -> {new} (대상: {count.count}권)")
            
            # 업데이트 실행
            response = supabase.table("childbook_items").update({"category": new}).eq("category", old).execute()
            # response.data가 리스트이므로 길이로 확인
            updated_count = len(response.data) if response.data else 0
            
            if updated_count > 0:
                print(f"  ✅ '{old}' -> '{new}': {updated_count}권 업데이트됨")    
                total_updated += updated_count
            else:
                print(f"  Running... '{old}' -> '{new}' (변경 없음)")
                
        except Exception as e:
            print(f"  ❌ '{old}' 업데이트 실패: {e}")
            
    print(f"\n🎉 총 {total_updated}권의 카테고리가 수정되었습니다.")

if __name__ == "__main__":
    update_categories()
