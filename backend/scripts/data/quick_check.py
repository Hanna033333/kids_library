from supabase_client import supabase

# 샘플 10권 확인
result = supabase.table('childbook_items').select(
    'title,category'
).eq('curation_tag', '겨울방학2026').limit(10).execute()

print("\n샘플 10권:")
print("-" * 60)
for book in result.data:
    print(f"{book['title'][:30]:30s} -> {book['category']}")
