"""'없음'으로 채워진 항목 수 확인"""
from supabase_client import supabase

res = supabase.table("childbook_items").select("pangyo_callno", count="exact").eq("pangyo_callno", "없음").execute()

count = res.count if hasattr(res, 'count') else len(res.data) if res.data else 0

print("=" * 60)
print("'없음'으로 채워진 항목")
print("=" * 60)
print(f"총 개수: {count:,}개")
print("=" * 60)

