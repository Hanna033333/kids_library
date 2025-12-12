"""
library_items 테이블 저장 테스트 (짧은 기간)
"""
from main import sync_library_books_child
from supabase_client import supabase

print("=" * 60)
print("library_items 테이블 저장 테스트 (짧은 기간)")
print("기간: 2024-12-01 ~ 2024-12-31")
print("=" * 60)
print()

try:
    # 먼저 현재 저장된 데이터 수 확인
    try:
        existing = supabase.table("library_items").select("*", count="exact").execute()
        count_before = existing.count if hasattr(existing, 'count') else len(existing.data) if existing.data else 0
        print(f"현재 library_items에 저장된 도서 수: {count_before}권")
    except Exception as e:
        print(f"기존 데이터 확인 중 오류 (테이블이 비어있을 수 있음): {e}")
        count_before = 0
    print()
    
    # 짧은 기간으로 테스트
    result = sync_library_books_child('2024-12-01', '2024-12-31')
    
    print()
    print("=" * 60)
    print(f"수집 및 저장 완료!")
    print(f"수집된 도서 수: {result.get('count', 0)}권")
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
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()







