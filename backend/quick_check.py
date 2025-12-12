from supabase_client import supabase

try:
    result = supabase.table("library_items").select("*", count="exact").execute()
    total_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
    print(f"현재 저장된 도서 수: {total_count:,}권")
    print(f"어제 완료: 15,525권")
    print(f"차이: {total_count - 15525:,}권")
except Exception as e:
    print(f"오류: {e}")




