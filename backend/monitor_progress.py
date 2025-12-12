"""
수집 진행 상황 모니터링 (5초마다 확인)
"""
from supabase_client import supabase
import time
import sys

def monitor_progress():
    initial_count = 15525  # 어제 완료된 수
    last_count = initial_count
    
    print("=" * 60)
    print("수집 진행 상황 모니터링 시작")
    print(f"기준 수: {initial_count:,}권")
    print("=" * 60)
    print()
    sys.stdout.flush()
    
    while True:
        try:
            result = supabase.table("library_items").select("*", count="exact").execute()
            current_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
            
            if current_count > last_count:
                added = current_count - last_count
                total_added = current_count - initial_count
                print(f"[{time.strftime('%H:%M:%S')}] ✅ 추가 수집: +{added:,}권 | 총 추가: +{total_added:,}권 | 전체: {current_count:,}권")
                sys.stdout.flush()
                last_count = current_count
            elif current_count == last_count:
                print(f"[{time.strftime('%H:%M:%S')}] 진행 중... (현재: {current_count:,}권)")
                sys.stdout.flush()
            
            time.sleep(5)  # 5초마다 확인
            
        except KeyboardInterrupt:
            print("\n모니터링 종료")
            break
        except Exception as e:
            print(f"오류: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_progress()




