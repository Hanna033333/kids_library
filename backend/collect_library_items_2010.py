"""
2010-01-01부터 판교 도서관 아동 도서 수집 및 library_items 테이블에 저장
"""
from main import sync_library_books_child
from supabase_client import supabase
import time
from datetime import datetime

def collect_library_items_from_2010():
    """
    2010-01-01부터 현재까지 판교 도서관 아동 도서 수집 및 저장
    연도별로 나눠서 수집하여 API 타임아웃 방지
    """
    print("=" * 60)
    print("판교 도서관 아동 도서 수집 및 library_items 저장")
    print("기간: 2010-01-01 ~ 2025-12-31")
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
    print("⚠️  주의: 연도별로 나눠서 수집합니다. 시간이 오래 걸릴 수 있습니다.")
    print("진행 상황은 콘솔에 표시됩니다.")
    print()
    
    start_time = time.time()
    total_count = 0
    
    # 연도별로 나눠서 수집 (2010년부터 2025년까지)
    years = list(range(2010, 2026))
    
    try:
        for year in years:
            start_dt = f"{year}-01-01"
            end_dt = f"{year}-12-31"
            
            print(f"\n{'='*60}")
            print(f"📅 {year}년 데이터 수집 시작...")
            print(f"{'='*60}")
            
            year_start_time = time.time()
            
            try:
                result = sync_library_books_child(start_dt, end_dt)
                year_count = result.get('count', 0)
                total_count += year_count
                
                year_elapsed = time.time() - year_start_time
                print(f"✅ {year}년 수집 완료: {year_count}권 (소요 시간: {year_elapsed:.2f}초)")
                
                # API 부하 방지를 위한 짧은 대기
                if year < years[-1]:  # 마지막 연도가 아니면
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ {year}년 수집 중 오류 발생: {e}")
                print("다음 연도로 계속 진행합니다...")
                continue
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print()
        print("=" * 60)
        print(f"✅ 전체 수집 및 저장 완료!")
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
        print(f"현재까지 수집된 도서 수: {total_count}권")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    collect_library_items_from_2010()


