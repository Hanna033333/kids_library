"""
필터링 조건 테스트: ISBN 또는 pangyo_callno가 없는 항목 확인
"""
from supabase_client import supabase

print("=" * 60)
print("필터링 조건 테스트")
print("=" * 60)
print()

# 전체 데이터 샘플 확인
print("1. 전체 데이터 샘플 (10개):")
items = supabase.table("childbook_items").select("id,isbn,pangyo_callno").limit(10).execute()
for item in items.data:
    isbn = item.get("isbn")
    pangyo_callno = item.get("pangyo_callno")
    has_isbn = isbn and len(str(isbn).strip()) > 0
    has_pangyo_callno = pangyo_callno and len(str(pangyo_callno).strip()) > 0
    print(f"  ID: {item['id']}, ISBN: {has_isbn}, pangyo_callno: {has_pangyo_callno}")

print()

# 필터링된 항목 수 확인
print("2. 필터링 조건 확인:")
print("   조건: ISBN이 없거나 pangyo_callno가 없는 항목")
print()

all_items = []
page = 0
page_size = 1000

while True:
    res = supabase.table("childbook_items").select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    all_items.extend(res.data)
    if len(res.data) < page_size:
        break
    page += 1

print(f"   전체 항목 수: {len(all_items):,}개")

filtered_items = []
for item in all_items:
    isbn = item.get("isbn")
    pangyo_callno = item.get("pangyo_callno")
    
    has_isbn = isbn and len(str(isbn).strip()) > 0
    has_pangyo_callno = pangyo_callno and len(str(pangyo_callno).strip()) > 0
    
    if not has_isbn or not has_pangyo_callno:
        filtered_items.append(item)

print(f"   필터링된 항목 수: {len(filtered_items):,}개")
print()

# 상세 통계
no_isbn = sum(1 for item in all_items if not (item.get("isbn") and len(str(item.get("isbn")).strip()) > 0))
no_pangyo_callno = sum(1 for item in all_items if not (item.get("pangyo_callno") and len(str(item.get("pangyo_callno")).strip()) > 0))
both_missing = sum(1 for item in all_items if not (item.get("isbn") and len(str(item.get("isbn")).strip()) > 0) and not (item.get("pangyo_callno") and len(str(item.get("pangyo_callno")).strip()) > 0))

print("3. 상세 통계:")
print(f"   ISBN 없음: {no_isbn:,}개")
print(f"   pangyo_callno 없음: {no_pangyo_callno:,}개")
print(f"   둘 다 없음: {both_missing:,}개")
print(f"   처리 대상 (ISBN 또는 pangyo_callno 없음): {len(filtered_items):,}개")
print("=" * 60)


