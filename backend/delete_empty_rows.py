"""
childbook_items 테이블에서 page, age, category, price, keywords가 모두 없는 행 삭제
"""
from supabase_client import supabase

print("=" * 60)
print("빈 필드가 있는 행 삭제")
print("=" * 60)
print()

try:
    # 먼저 전체 데이터 수 확인
    print("전체 데이터 수 확인 중...")
    count_result = supabase.table("childbook_items").select("*", count="exact").execute()
    total_count = count_result.count if hasattr(count_result, 'count') else 0
    print(f"전체 데이터 수: {total_count}건")
    print()
    
    # 페이지네이션으로 데이터 조회 및 삭제
    print("삭제 대상 검색 및 삭제 시작...")
    print("-" * 60)
    
    deleted_count = 0
    error_count = 0
    page_size = 1000
    offset = 0
    
    while True:
        # 페이지별로 데이터 조회
        data = supabase.table("childbook_items").select("*").range(offset, offset + page_size - 1).execute()
        
        if not data.data or len(data.data) == 0:
            break
        
        # 삭제할 행 찾기 및 삭제
        for item in data.data:
            page = item.get('page')
            age = item.get('age')
            category = item.get('category')
            price = item.get('price')
            keywords = item.get('keywords')
            
            # 모두 None이거나 빈 값인지 확인
            if (not page or page is None) and \
               (not age or age is None) and \
               (not category or category is None) and \
               (not price or price is None) and \
               (not keywords or keywords is None):
                try:
                    supabase.table("childbook_items").delete().eq("id", item.get('id')).execute()
                    deleted_count += 1
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:
                        print(f"  ID {item.get('id')} 삭제 오류: {e}")
        
        offset += page_size
        
        if offset % 5000 == 0:
            print(f"  {offset}건 처리 중... (삭제됨: {deleted_count}건)")
        
        # 마지막 페이지인 경우 종료
        if len(data.data) < page_size:
            break
    
    print("-" * 60)
    print(f"✅ 삭제 완료!")
    print(f"   삭제됨: {deleted_count}건")
    print(f"   오류: {error_count}건")
    
    # 삭제 후 데이터 수 확인
    try:
        updated = supabase.table("childbook_items").select("*", count="exact").execute()
        count_after = updated.count if hasattr(updated, 'count') else 0
        print(f"\n삭제 후 총 도서 수: {count_after}권 (-{total_count - count_after})")
    except Exception as e:
        print(f"\n최종 데이터 확인 중 오류: {e}")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

