"""
childbook_items 샘플 데이터 확인
"""
from supabase_client import supabase

print("=" * 60)
print("childbook_items 샘플 데이터 확인")
print("=" * 60)
print()

# ISBN이 없는 항목 10개 샘플
try:
    res = supabase.table("childbook_items").select("id, title, author, isbn").limit(100).execute()
    
    no_isbn_items = []
    for item in res.data:
        isbn = item.get("isbn")
        if not isbn or (isbn and len(str(isbn).strip()) == 0):
            no_isbn_items.append(item)
            if len(no_isbn_items) >= 10:
                break
    
    print(f"ISBN이 없는 항목 샘플 {len(no_isbn_items)}개:")
    print()
    
    for item in no_isbn_items:
        print(f"ID: {item.get('id')}")
        print(f"  제목: {item.get('title', '')[:50]}")
        print(f"  저자: {item.get('author', '')[:30]}")
        print(f"  ISBN: {item.get('isbn') or '(없음)'}")
        print("-" * 60)
        
except Exception as e:
    print(f"오류: {e}")

