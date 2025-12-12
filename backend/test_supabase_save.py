from main import sync_library_books_child
import time

print("=" * 60)
print("판교 도서관 아동 도서 수집 및 Supabase 저장 테스트")
print("기간: 2010-01-01 ~ 2025-12-31")
print("=" * 60)
print()

start_time = time.time()

try:
    result = sync_library_books_child('2010-01-01', '2025-12-31')
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print()
    print("=" * 60)
    print(f"수집 및 저장 완료!")
    print(f"저장된 도서 수: {result.get('count', 0)}권")
    print(f"소요 시간: {elapsed_time:.2f}초 ({elapsed_time/60:.2f}분)")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()









