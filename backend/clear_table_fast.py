"""
더 빠른 방법으로 테이블 비우기
"""
from supabase_client import supabase

print("=" * 60)
print("테이블 데이터 삭제 (빠른 방법)")
print("=" * 60)
print()

try:
    # 전체 데이터 수 확인
    count_result = supabase.table("childbook_items").select("*", count="exact").execute()
    count_before = count_result.count if hasattr(count_result, 'count') else 0
    print(f"삭제 전 총 도서 수: {count_before}건")
    print()
    
    if count_before == 0:
        print("삭제할 데이터가 없습니다.")
        exit(0)
    
    print("데이터 삭제 중... (이 작업은 시간이 걸릴 수 있습니다)")
    print("-" * 60)
    
    # 더 큰 배치로 삭제
    deleted = 0
    batch_size = 500
    
    while True:
        # ID만 조회
        data = supabase.table("childbook_items").select("id").limit(batch_size).execute()
        
        if not data.data or len(data.data) == 0:
            break
        
        # 배치 삭제
        for item in data.data:
            try:
                supabase.table("childbook_items").delete().eq("id", item['id']).execute()
                deleted += 1
            except Exception as e:
                print(f"  삭제 오류: {e}")
        
        if deleted % 500 == 0:
            print(f"  {deleted}건 삭제 중...")
        
        # 더 이상 데이터가 없으면 종료
        if len(data.data) < batch_size:
            break
    
    print("-" * 60)
    print(f"✅ {deleted}건 삭제 완료")
    
    # 확인
    count_result = supabase.table("childbook_items").select("*", count="exact").execute()
    count_after = count_result.count if hasattr(count_result, 'count') else 0
    print(f"\n삭제 후 총 도서 수: {count_after}건")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()







