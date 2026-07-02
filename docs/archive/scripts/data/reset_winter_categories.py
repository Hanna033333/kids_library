"""
겨울방학2026 도서 카테고리 초기화 (NULL로)
"""
from supabase_client import supabase

# 카테고리를 NULL로 초기화
result = supabase.table('childbook_items').update({
    'category': None
}).eq('curation_tag', '겨울방학2026').execute()

print(f"✅ {len(result.data)}권의 카테고리를 초기화했습니다.")
print("이제 recategorize_winter_safe.py를 다시 실행하세요.")
