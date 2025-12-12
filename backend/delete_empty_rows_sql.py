"""
SQL 쿼리를 사용해서 page, age, category, price, keywords가 모두 NULL인 행 삭제
"""
from supabase_client import supabase

print("=" * 60)
print("빈 필드가 있는 행 삭제 (SQL 쿼리 사용)")
print("=" * 60)
print()

try:
    # 먼저 전체 데이터 수 확인
    print("전체 데이터 수 확인 중...")
    count_result = supabase.table("childbook_items").select("*", count="exact").execute()
    count_before = count_result.count if hasattr(count_result, 'count') else 0
    print(f"삭제 전 총 도서 수: {count_before}건")
    print()
    
    # 삭제 대상 수 확인
    print("삭제 대상 검색 중...")
    # page, age, category, price, keywords가 모두 NULL인 행 찾기
    empty_rows = supabase.table("childbook_items").select("id").is_("page", "null").is_("age", "null").is_("category", "null").is_("price", "null").is_("keywords", "null").execute()
    
    delete_count = len(empty_rows.data) if empty_rows.data else 0
    print(f"삭제 대상: {delete_count}건")
    print()
    
    if delete_count == 0:
        print("삭제할 행이 없습니다.")
    else:
        print("삭제 시작...")
        print("-" * 60)
        
        # ID 목록 추출
        delete_ids = [item['id'] for item in empty_rows.data]
        
        # 배치로 삭제 (한 번에 너무 많이 삭제하면 문제가 될 수 있음)
        batch_size = 100
        deleted = 0
        errors = 0
        
        for i in range(0, len(delete_ids), batch_size):
            batch = delete_ids[i:i+batch_size]
            for id_val in batch:
                try:
                    supabase.table("childbook_items").delete().eq("id", id_val).execute()
                    deleted += 1
                except Exception as e:
                    errors += 1
                    if errors <= 5:
                        print(f"  ID {id_val} 삭제 오류: {e}")
            
            if (i + batch_size) % 1000 == 0 or i + batch_size >= len(delete_ids):
                print(f"  {min(i + batch_size, len(delete_ids))}/{len(delete_ids)} 삭제 중...")
        
        print("-" * 60)
        print(f"✅ 삭제 완료!")
        print(f"   삭제됨: {deleted}건")
        print(f"   오류: {errors}건")
        
        # 삭제 후 데이터 수 확인
        try:
            updated = supabase.table("childbook_items").select("*", count="exact").execute()
            count_after = updated.count if hasattr(updated, 'count') else 0
            print(f"\n삭제 후 총 도서 수: {count_after}권 (-{count_before - count_after})")
        except Exception as e:
            print(f"\n최종 데이터 확인 중 오류: {e}")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()







