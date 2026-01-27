from supabase_client import supabase
import json

# 카테고리별 분포
result = supabase.table('childbook_items').select('category').eq('curation_tag', '겨울방학2026').execute()

categories = {}
for book in result.data:
    cat = book.get('category', 'N/A')
    categories[cat] = categories.get(cat, 0) + 1

print(json.dumps(categories, ensure_ascii=False, indent=2))
print(f"\n총 {len(result.data)}권")
