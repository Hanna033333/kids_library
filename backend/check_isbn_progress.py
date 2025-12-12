"""
ISBN 채우기 진행 상황 확인
"""
from supabase_client import supabase

print("=" * 60)
print("ISBN 채우기 진행 상황 확인")
print("=" * 60)
print()

try:
    # 전체 항목 수
    total_res = supabase.table("childbook_items").select("*", count="exact").execute()
    total_count = total_res.count if hasattr(total_res, 'count') else len(total_res.data) if total_res.data else 0
    
    # ISBN이 있는 항목 수
    # ISBN이 있는 항목은 isbn 필드가 있고 비어있지 않은 항목
    all_items = []
    page = 0
    page_size = 1000
    
    while True:
        res = supabase.table("childbook_items").select("id, isbn").range(page * page_size, (page + 1) * page_size - 1).execute()
        if not res.data:
            break
        all_items.extend(res.data)
        if len(res.data) < page_size:
            break
        page += 1
    
    has_isbn_count = sum(1 for item in all_items if item.get("isbn") and len(str(item.get("isbn")).strip()) > 0)
    no_isbn_count = total_count - has_isbn_count
    
    print(f"전체 항목: {total_count:,}개")
    print(f"ISBN 있음: {has_isbn_count:,}개 ({has_isbn_count/total_count*100:.1f}%)")
    print(f"ISBN 없음: {no_isbn_count:,}개 ({no_isbn_count/total_count*100:.1f}%)")
    print()
    
    if has_isbn_count > 0:
        print(f"✅ 진행률: {has_isbn_count/total_count*100:.1f}%")
    else:
        print("⚠️  아직 ISBN이 채워진 항목이 없습니다.")
        
except Exception as e:
    print(f"오류: {e}")



