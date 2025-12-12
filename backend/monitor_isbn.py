"""
ISBN 채우기 진행 상황 모니터링
"""
from supabase_client import supabase
import time

print("=" * 60)
print("ISBN 채우기 진행 상황 모니터링")
print("=" * 60)
print("Ctrl+C를 눌러 종료하세요.")
print()

initial_has_isbn = None
check_count = 0

try:
    while True:
        try:
            # 전체 항목 수
            total_res = supabase.table("childbook_items").select("*", count="exact").execute()
            total_count = total_res.count if hasattr(total_res, 'count') else len(total_res.data) if total_res.data else 0
            
            # ISBN이 있는 항목 수 (정확히 계산)
            # 전체 데이터를 페이지별로 확인
            has_isbn_count = 0
            page = 0
            page_size = 1000
            
            while True:
                res = supabase.table("childbook_items").select("isbn").range(page * page_size, (page + 1) * page_size - 1).execute()
                if not res.data:
                    break
                for item in res.data:
                    isbn = item.get("isbn")
                    if isbn and len(str(isbn).strip()) > 0:
                        has_isbn_count += 1
                if len(res.data) < page_size:
                    break
                page += 1
            
            estimated_has_isbn = has_isbn_count
            
            if initial_has_isbn is None:
                initial_has_isbn = estimated_has_isbn
            
            check_count += 1
            progress = estimated_has_isbn / total_count * 100 if total_count > 0 else 0
            added = estimated_has_isbn - initial_has_isbn
            
            print(f"[{check_count}] 전체: {total_count:,}개 | ISBN 있음: {estimated_has_isbn:,}개 ({progress:.1f}%) | 추가됨: +{added}개")
            
            time.sleep(30)  # 30초마다 확인
            
        except KeyboardInterrupt:
            print("\n모니터링 종료")
            break
        except Exception as e:
            print(f"확인 중 오류: {e}")
            time.sleep(30)

except KeyboardInterrupt:
    print("\n모니터링 종료")



