from supabase_client import supabase

# 전체 항목 수
total = supabase.table("childbook_items").select("*", count="exact").execute()
total_count = total.count if hasattr(total, 'count') else len(total.data) if total.data else 0

# ISBN이 있는 항목 수 (샘플링)
sample = supabase.table("childbook_items").select("isbn").limit(1000).execute()
has_isbn = sum(1 for item in sample.data if item.get("isbn") and len(str(item.get("isbn")).strip()) > 0)
sample_size = len(sample.data)

# 추정
estimated_has_isbn = int(has_isbn / sample_size * total_count) if sample_size > 0 else 0
estimated_no_isbn = total_count - estimated_has_isbn

print(f"전체: {total_count:,}개")
print(f"ISBN 있음 (추정): {estimated_has_isbn:,}개 ({estimated_has_isbn/total_count*100:.1f}%)")
print(f"ISBN 없음 (추정): {estimated_no_isbn:,}개 ({estimated_no_isbn/total_count*100:.1f}%)")



