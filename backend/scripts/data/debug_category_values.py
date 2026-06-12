from supabase_client import supabase

# 처음 5권의 category 값을 정확히 확인
result = supabase.table('childbook_items').select('id,title,category').eq('curation_tag', '겨울방학2026').limit(5).execute()

print("처음 5권의 category 값:")
for book in result.data:
    cat = book.get('category')
    print(f"  {book['title']}")
    print(f"    category: {repr(cat)} (type: {type(cat).__name__})")
    print(f"    is None: {cat is None}")
    print(f"    == None: {cat == None}")
    print()
