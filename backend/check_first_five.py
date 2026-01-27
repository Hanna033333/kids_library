from supabase_client import supabase

# 처음 5권의 카테고리 직접 확인
result = supabase.table('childbook_items').select('title,category').eq('curation_tag', '겨울방학2026').limit(5).execute()

print("처음 5권:")
for book in result.data:
    print(f"  {book['title']}: {book.get('category')}")
