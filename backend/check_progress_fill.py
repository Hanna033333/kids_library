"""진행 상황 확인"""
from supabase_client import supabase

res = supabase.table("childbook_items").select("pangyo_callno", count="exact").execute()
total = res.count if hasattr(res, 'count') else len(res.data) if res.data else 0

res2 = supabase.table("childbook_items").select("id", count="exact").eq("pangyo_callno", "없음").execute()
no_callno = res2.count if hasattr(res2, 'count') else len(res2.data) if res2.data else 0

res3 = supabase.table("childbook_items").select("id", count="exact").not_.is_("pangyo_callno", "null").neq("pangyo_callno", "없음").execute()
has_callno = res3.count if hasattr(res3, 'count') else len(res3.data) if res3.data else 0

print("=" * 60)
print("진행 상황")
print("=" * 60)
print(f"전체 항목: {total:,}개")
print(f"청구기호 있음: {has_callno:,}개")
print(f"청구기호 없음/없음: {no_callno:,}개")
print("=" * 60)

