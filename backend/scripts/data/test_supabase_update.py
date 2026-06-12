"""
Supabase UPDATE 권한 테스트
"""
from supabase_client import supabase

# 첫 번째 책 가져오기
result = supabase.table('childbook_items').select('id,title,category').eq('curation_tag', '겨울방학2026').limit(1).execute()

book = result.data[0]
print(f"책 ID: {book['id']}")
print(f"제목: {book['title']}")
print(f"현재 카테고리: {book.get('category')}")

# 테스트 업데이트
print("\n테스트 업데이트 시도...")
try:
    update_result = supabase.table('childbook_items').update({
        'category': '동화'
    }).eq('id', book['id']).execute()
    
    print(f"✅ 성공!")
    print(f"응답 데이터: {update_result.data}")
    
    # 다시 조회해서 확인
    check = supabase.table('childbook_items').select('category').eq('id', book['id']).execute()
    print(f"\n확인: {check.data[0]['category']}")
    
except Exception as e:
    print(f"❌ 실패: {e}")
    import traceback
    traceback.print_exc()
