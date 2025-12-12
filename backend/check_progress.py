"""
수집 진행 상황 확인
"""
from supabase_client import supabase
from datetime import datetime

print("=" * 60)
print("판교 도서관 아동 도서 수집 진행 상황 확인")
print("=" * 60)
print()

try:
    # 현재 저장된 데이터 수 확인
    result = supabase.table("library_items").select("*", count="exact").execute()
    count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
    
    print(f"현재 library_items에 저장된 도서 수: {count}권")
    print()
    
    # 최근 수집된 데이터 확인 (최근 5개)
    recent = supabase.table("library_items").select("*").order("created_at", desc=True).limit(5).execute()
    
    if recent.data:
        print("최근 수집된 도서 (최근 5개):")
        for i, book in enumerate(recent.data[:5], 1):
            print(f"{i}. {book.get('title', 'N/A')} - {book.get('author', 'N/A')}")
            print(f"   ISBN: {book.get('isbn13', 'N/A')}, 청구기호: {book.get('callno', 'N/A')}")
            if book.get('created_at'):
                print(f"   수집 시간: {book.get('created_at')}")
            print()
    
    # 연도별 통계 (isbn13이 있는 경우)
    print("=" * 60)
    print("참고: 전체 수집이 완료되면 더 많은 데이터가 표시됩니다.")
    print("=" * 60)
    
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()





