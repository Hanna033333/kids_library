"""
진행 상황을 3번 확인 (30초 간격)
"""
from supabase_client import supabase
import time

for i in range(3):
    try:
        # 전체 항목 수
        total_res = supabase.table("childbook_items").select("*", count="exact").execute()
        total_count = total_res.count if hasattr(total_res, 'count') else 3742
        
        # ISBN이 있는 항목 수 (샘플링)
        sample = supabase.table("childbook_items").select("isbn").limit(1000).execute()
        has_isbn_count = sum(1 for item in sample.data if item.get("isbn") and len(str(item.get("isbn")).strip()) > 0)
        sample_size = len(sample.data)
        
        # 추정
        estimated_has_isbn = int(has_isbn_count / sample_size * total_count) if sample_size > 0 else 0
        progress = estimated_has_isbn / total_count * 100 if total_count > 0 else 0
        remaining = total_count - estimated_has_isbn
        
        print(f"[체크 {i+1}/3] ISBN 있음: {estimated_has_isbn:,}개 ({progress:.1f}%) | 남음: {remaining:,}개")
        
        if i < 2:  # 마지막 체크 후에는 대기 안함
            time.sleep(30)
            
    except Exception as e:
        print(f"오류: {e}")
        break

print("\n완료! 최종 확인을 위해 'python quick_check_isbn.py'를 실행하세요.")



