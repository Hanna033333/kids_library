"""
최근 업데이트된 항목 확인 (스크립트가 작동하는지 확인)
"""
from supabase_client import supabase
from datetime import datetime, timedelta

print("=" * 60)
print("최근 업데이트된 항목 확인")
print("=" * 60)
print()

# 최근 5분 이내에 업데이트된 항목 확인
# updated_at 필드가 있다면 사용, 없으면 id로 최신 항목 확인
try:
    # ISBN이 있는 항목 중 최신 항목 10개 확인
    res = supabase.table("childbook_items").select("id,isbn,title,updated_at").not_.is_("isbn", "null").order("id", desc=True).limit(10).execute()
    
    print("최근 ISBN이 추가된 항목 (최신 10개):")
    print("-" * 60)
    for item in res.data:
        isbn = item.get("isbn", "")
        title = item.get("title", "")[:50]
        item_id = item.get("id")
        updated = item.get("updated_at", "")
        print(f"ID: {item_id} | ISBN: {isbn} | 제목: {title}")
    print()
    
    # 둘 다 없는 항목 중 샘플 확인
    print("처리 대상 항목 샘플 (둘 다 없는 항목 5개):")
    print("-" * 60)
    all_items = []
    page = 0
    page_size = 1000
    
    while len(all_items) < 5:
        res = supabase.table("childbook_items").select("id,isbn,pangyo_callno,title").range(page * page_size, (page + 1) * page_size - 1).execute()
        if not res.data:
            break
        
        for item in res.data:
            isbn = item.get("isbn")
            pangyo_callno = item.get("pangyo_callno")
            has_isbn = isbn and len(str(isbn).strip()) > 0
            has_pangyo = pangyo_callno and len(str(pangyo_callno).strip()) > 0
            
            if not has_isbn and not has_pangyo:
                all_items.append(item)
                if len(all_items) >= 5:
                    break
        
        if len(res.data) < page_size:
            break
        page += 1
    
    for item in all_items:
        print(f"ID: {item.get('id')} | 제목: {item.get('title', '')[:50]}")
    
except Exception as e:
    print(f"오류: {e}")

print()
print("=" * 60)

