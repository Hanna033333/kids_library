"""
수집 진행 상황 확인
"""
from supabase_client import supabase
import time

print("=" * 60)
print("수집 진행 상황 확인")
print("=" * 60)
print()

try:
    result = supabase.table("library_items").select("*", count="exact").execute()
    current_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
    
    initial_count = 15525  # 어제 완료된 수
    
    print(f"어제 완료: {initial_count:,}권")
    print(f"현재 저장: {current_count:,}권")
    print()
    
    if current_count > initial_count:
        added = current_count - initial_count
        print(f"✅ 오늘 추가 수집: +{added:,}권")
        print(f"진행률: {added / 100:.0f}배치 완료 (100권 = 1배치)")
    elif current_count == initial_count:
        print("⚠️  아직 수집이 시작되지 않았거나 진행 중입니다.")
        print("잠시 후 다시 확인해주세요.")
    else:
        print("⚠️  데이터가 감소했습니다. 확인이 필요합니다.")
    
    print()
    print("=" * 60)
    
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()




