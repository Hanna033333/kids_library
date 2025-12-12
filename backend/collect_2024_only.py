"""
2024년 판교 도서관 아동 도서 수집 및 library_items 테이블에 저장
"""
from main import sync_library_books_child
from supabase_client import supabase
import time

print("=" * 60)
print("판교 도서관 아동 도서 수집 및 library_items 저장")
print("기간: 2024-01-01 ~ 2024-12-31")
print("=" * 60)
print()

# 현재 저장된 데이터 수 확인
try:
    existing = supabase.table("library_items").select("*", count="exact").execute()
    count_before = existing.count if hasattr(existing, 'count') else len(existing.data) if existing.data else 0
    print(f"현재 library_items에 저장된 도서 수: {count_before}권")
except Exception as e:
    print(f"기존 데이터 확인 중 오류: {e}")
    count_before = 0

print()
print("⚠️  2024년 데이터 수집을 시작합니다...")
print("분기별로 나눠서 수집합니다.")
print()

start_time = time.time()
total_count = 0

# 분기별로 나눠서 수집 (페이지 크기를 줄였으므로 분기별로 가능)
quarters = [
    ('2024-01-01', '2024-03-31', '1분기'),
    ('2024-04-01', '2024-06-30', '2분기'),
    ('2024-07-01', '2024-09-30', '3분기'),
    ('2024-10-01', '2024-12-31', '4분기'),
]

try:
    for start_dt, end_dt, quarter_name in quarters:
        print(f"\n{'='*60}")
        print(f"📅 2024년 {quarter_name} 수집 시작...")
        print(f"{'='*60}")
        
        quarter_start_time = time.time()
        
        try:
            result = sync_library_books_child(start_dt, end_dt)
            quarter_count = result.get('count', 0)
            total_count += quarter_count
            
            quarter_elapsed = time.time() - quarter_start_time
            print(f"✅ {quarter_name} 수집 완료: {quarter_count}권 (소요 시간: {quarter_elapsed:.2f}초)")
            
            # API 부하 방지를 위한 대기
            if quarter_name != '4분기':
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ {quarter_name} 수집 중 오류 발생: {e}")
            print("다음 분기로 계속 진행합니다...")
            continue
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print()
    print("=" * 60)
    print(f"✅ 수집 및 저장 완료!")
    print(f"총 수집된 도서 수: {total_count}권")
    print(f"총 소요 시간: {elapsed_time:.2f}초 ({elapsed_time/60:.2f}분)")
    print("=" * 60)
    
    # 저장 후 데이터 수 확인
    try:
        updated = supabase.table("library_items").select("*", count="exact").execute()
        count_after = updated.count if hasattr(updated, 'count') else len(updated.data) if updated.data else 0
        print(f"\n저장 후 library_items에 저장된 도서 수: {count_after}권")
        print(f"추가된 도서 수: {count_after - count_before}권")
        
        # 샘플 데이터 확인
        sample = supabase.table("library_items").select("*").limit(5).execute()
        if sample.data:
            print(f"\n샘플 데이터 (최근 5개):")
            for i, book in enumerate(sample.data[:5], 1):
                print(f"{i}. {book.get('title', 'N/A')} - {book.get('author', 'N/A')}")
                print(f"   ISBN: {book.get('isbn13', 'N/A')}, 청구기호: {book.get('callno', 'N/A')}")
    except Exception as e:
        print(f"\n저장 후 데이터 확인 중 오류: {e}")
    
except KeyboardInterrupt:
    print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

