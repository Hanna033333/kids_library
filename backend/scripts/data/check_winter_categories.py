"""
겨울방학2026 도서 카테고리 분류 결과 확인
"""
from supabase_client import supabase

# 카테고리별 분포 확인
result = supabase.table('childbook_items').select(
    'category'
).eq('curation_tag', '겨울방학2026').execute()

if result.data:
    categories = {}
    for book in result.data:
        cat = book.get('category', 'N/A')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("=" * 60)
    print("겨울방학2026 도서 카테고리 분류 결과")
    print("=" * 60)
    print(f"\n총 {len(result.data)}권\n")
    
    # 카테고리별 정렬 (많은 순)
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(result.data)) * 100
        print(f"  {cat:8s}: {count:3d}권 ({percentage:5.1f}%)")
    
    print("\n" + "=" * 60)
else:
    print("데이터 없음")
