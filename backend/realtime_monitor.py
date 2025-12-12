"""
실시간 ISBN 수집 모니터링 (10초마다 확인)
"""
from supabase_client import supabase
import time
import sys

print("=" * 60)
print("실시간 ISBN 수집 모니터링")
print("=" * 60)
print()

last_count = 0
check_num = 0

try:
    while True:
        check_num += 1
        
        # 샘플링으로 빠르게 확인
        sample = supabase.table("childbook_items").select("isbn").limit(1000).execute()
        has_isbn = sum(1 for item in sample.data if item.get("isbn") and len(str(item.get("isbn")).strip()) > 0)
        estimated_total = int(has_isbn / len(sample.data) * 3742) if len(sample.data) > 0 else 0
        
        progress = estimated_total / 3742 * 100
        added = estimated_total - last_count
        
        timestamp = time.strftime("%H:%M:%S")
        
        if added > 0:
            print(f"[{timestamp}] 📚 ISBN: {estimated_total:,}개 ({progress:.1f}%) | +{added}개 추가")
        else:
            print(f"[{timestamp}] 📊 ISBN: {estimated_total:,}개 ({progress:.1f}%)")
        
        last_count = estimated_total
        
        sys.stdout.flush()
        time.sleep(10)
        
except KeyboardInterrupt:
    print("\n\n모니터링 종료")
except Exception as e:
    print(f"\n오류: {e}")



