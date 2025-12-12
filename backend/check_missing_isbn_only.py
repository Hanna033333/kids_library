"""
ISBN만 없는 항목 수 확인
"""
from supabase_client import supabase

print("=" * 60)
print("ISBN만 없는 항목 확인")
print("=" * 60)
print()

# 전체 항목 수
total = supabase.table("childbook_items").select("*", count="exact").execute()
total_count = total.count if hasattr(total, 'count') else len(total.data) if total.data else 0

print(f"전체 childbook_items: {total_count:,}개")
print()

# ISBN이 없는 항목만 카운트
missing_isbn_count = 0
page = 0
page_size = 1000

print("ISBN 없는 항목 확인 중...")
while True:
    res = supabase.table("childbook_items").select("isbn").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
    for item in res.data:
        isbn = item.get("isbn")
        has_isbn = isbn and len(str(isbn).strip()) > 0
        if not has_isbn:
            missing_isbn_count += 1
    
    if len(res.data) < page_size:
        break
    page += 1

print()
print("=" * 60)
print(f"ISBN 없는 항목: {missing_isbn_count:,}개 ({missing_isbn_count/total_count*100:.1f}%)")
print("=" * 60)

