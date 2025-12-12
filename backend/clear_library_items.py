"""
library_items 테이블 전체 삭제
"""
from supabase_client import supabase

print("=" * 60)
print("library_items 테이블 전체 삭제")
print("=" * 60)
print()

try:
    # 현재 데이터 수 확인
    existing = supabase.table("library_items").select("*", count="exact").execute()
    count_before = existing.count if hasattr(existing, 'count') else len(existing.data) if existing.data else 0
    print(f"현재 저장된 도서 수: {count_before}권")
    print()
    
    # 전체 삭제 (isbn13 기준으로 삭제)
    # 먼저 모든 isbn13 가져오기
    all_books = supabase.table("library_items").select("isbn13").execute()
    isbn_list = [book.get("isbn13") for book in all_books.data if book.get("isbn13")]
    
    if isbn_list:
        # 배치로 삭제
        deleted_count = 0
        for isbn in isbn_list:
            try:
                supabase.table("library_items").delete().eq("isbn13", isbn).execute()
                deleted_count += 1
            except Exception as e:
                print(f"삭제 실패 (ISBN: {isbn}): {e}")
        print(f"✅ {deleted_count}건 삭제 완료")
    else:
        print("삭제할 데이터가 없습니다.")
    print("✅ library_items 테이블 전체 삭제 완료!")
    
    # 삭제 후 확인
    after = supabase.table("library_items").select("*", count="exact").execute()
    count_after = after.count if hasattr(after, 'count') else len(after.data) if after.data else 0
    print(f"삭제 후 도서 수: {count_after}권")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

