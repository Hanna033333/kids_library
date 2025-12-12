"""
ISBN 매칭 상태 확인
"""
from supabase_client import supabase

print("=" * 60)
print("ISBN 매칭 상태 확인")
print("=" * 60)
print()

# 전체 childbook_items 수
total = supabase.table("childbook_items").select("*", count="exact").execute()
total_count = total.count if hasattr(total, 'count') else len(total.data) if total.data else 0

# owned=True인 항목 수
owned = supabase.table("childbook_items").select("*", count="exact").eq("owned", True).execute()
owned_count = owned.count if hasattr(owned, 'count') else len(owned.data) if owned.data else 0

# ISBN이 있는 항목 수
has_isbn = supabase.table("childbook_items").select("isbn").limit(1000).execute()
has_isbn_count = sum(1 for item in has_isbn.data if item.get("isbn") and len(str(item.get("isbn")).strip()) > 0)
estimated_has_isbn = int(has_isbn_count / len(has_isbn.data) * total_count) if len(has_isbn.data) > 0 else 0

# pangyo_callno가 있는 항목 수
has_callno = supabase.table("childbook_items").select("pangyo_callno").limit(1000).execute()
has_callno_count = sum(1 for item in has_callno.data if item.get("pangyo_callno") and len(str(item.get("pangyo_callno")).strip()) > 0)
estimated_has_callno = int(has_callno_count / len(has_callno.data) * total_count) if len(has_callno.data) > 0 else 0

print(f"전체 childbook_items: {total_count:,}개")
print(f"매칭됨 (owned=True): {owned_count:,}개 ({owned_count/total_count*100:.1f}%)")
print(f"ISBN 있음 (추정): {estimated_has_isbn:,}개 ({estimated_has_isbn/total_count*100:.1f}%)")
print(f"pangyo_callno 있음 (추정): {estimated_has_callno:,}개 ({estimated_has_callno/total_count*100:.1f}%)")
print()

if owned_count < estimated_has_isbn:
    print(f"⚠️  매칭이 완료되지 않았습니다!")
    print(f"   ISBN이 있는 항목: {estimated_has_isbn:,}개")
    print(f"   매칭된 항목: {owned_count:,}개")
    print(f"   남은 작업: {estimated_has_isbn - owned_count:,}개")
else:
    print("✅ 매칭이 완료된 것으로 보입니다.")


