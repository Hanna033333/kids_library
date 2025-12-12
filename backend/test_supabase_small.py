from main import sync_library_books_child
from supabase_client import supabase

print("=" * 60)
print("Supabase 저장 테스트 (짧은 기간)")
print("기간: 2024-12-01 ~ 2024-12-31")
print("=" * 60)
print()

try:
    # 먼저 현재 저장된 데이터 수 확인
    existing = supabase.table("childbook_items").select("*", count="exact").execute()
    print(f"현재 Supabase에 저장된 도서 수: {existing.count if hasattr(existing, 'count') else len(existing.data)}권")
    print()
    
    # 짧은 기간으로 테스트
    result = sync_library_books_child('2024-12-01', '2024-12-31')
    
    print()
    print("=" * 60)
    print(f"수집 및 저장 완료!")
    print(f"수집된 도서 수: {result.get('count', 0)}권")
    print("=" * 60)
    
    # 저장 후 데이터 수 확인
    updated = supabase.table("childbook_items").select("*", count="exact").execute()
    print(f"\n저장 후 Supabase에 저장된 도서 수: {updated.count if hasattr(updated, 'count') else len(updated.data)}권")
    
    # 샘플 데이터 확인
    sample = supabase.table("childbook_items").select("*").limit(5).execute()
    if sample.data:
        print(f"\n샘플 데이터 (최근 5개):")
        for i, book in enumerate(sample.data[:5], 1):
            print(f"{i}. {book.get('title', 'N/A')} - {book.get('author', 'N/A')}")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()









