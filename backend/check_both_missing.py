"""
ISBN과 pangyo_callno 둘 다 없는 항목 수 확인
"""
from supabase_client import supabase

print("=" * 60)
print("ISBN과 pangyo_callno 둘 다 없는 항목 확인")
print("=" * 60)
print()

# 전체 항목 수
total = supabase.table("childbook_items").select("*", count="exact").execute()
total_count = total.count if hasattr(total, 'count') else len(total.data) if total.data else 0

print(f"전체 childbook_items: {total_count:,}개")
print()

# 둘 다 없는 항목만 카운트
both_missing_count = 0
page = 0
page_size = 1000

print("둘 다 없는 항목 확인 중...")
while True:
    res = supabase.table("childbook_items").select("isbn,pangyo_callno").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
    for item in res.data:
        isbn = item.get("isbn")
        pangyo_callno = item.get("pangyo_callno")
        
        has_isbn = isbn and len(str(isbn).strip()) > 0
        has_pangyo_callno = pangyo_callno and len(str(pangyo_callno).strip()) > 0
        
        if not has_isbn and not has_pangyo_callno:
            both_missing_count += 1
    
    if len(res.data) < page_size:
        break
    page += 1

print()
print("=" * 60)
print(f"ISBN과 pangyo_callno 둘 다 없는 항목: {both_missing_count:,}개 ({both_missing_count/total_count*100:.1f}%)")
print("=" * 60)

