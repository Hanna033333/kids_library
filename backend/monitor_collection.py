"""
수집 진행 상황 모니터링
"""
from supabase_client import supabase
import time

print("=" * 60)
print("수집 진행 상황 모니터링")
print("=" * 60)
print()
print("Ctrl+C를 눌러 종료하세요.")
print()

initial_count = None
last_count = None
check_count = 0

try:
    while True:
        try:
            result = supabase.table("library_items").select("*", count="exact").execute()
            current_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
            
            if initial_count is None:
                initial_count = current_count
                last_count = current_count
                print(f"초기 저장된 도서 수: {current_count:,}권")
                print()
            
            check_count += 1
            
            if current_count > last_count:
                added = current_count - last_count
                total_added = current_count - initial_count
                print(f"[{check_count}] ✅ {current_count:,}권 (+{added}권, 총 +{total_added}권)")
            else:
                print(f"[{check_count}] 대기 중... {current_count:,}권")
            
            last_count = current_count
            
            time.sleep(10)  # 10초마다 확인
            
        except KeyboardInterrupt:
            print("\n모니터링 종료")
            break
        except Exception as e:
            print(f"확인 중 오류: {e}")
            time.sleep(10)

except KeyboardInterrupt:
    print("\n모니터링 종료")



