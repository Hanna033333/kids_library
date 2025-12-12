from main import sync_childbook_recommendations
from supabase_client import supabase

print("=" * 60)
print("어린이 도서 연구회 추천 도서 수집 및 저장 테스트")
print("=" * 60)
print()

try:
    # 먼저 현재 저장된 데이터 수 확인
    try:
        existing = supabase.table("childbook_items").select("*", count="exact").execute()
        count_before = existing.count if hasattr(existing, 'count') else len(existing.data) if existing.data else 0
        print(f"현재 childbook_items에 저장된 도서 수: {count_before}권")
    except Exception as e:
        print(f"기존 데이터 확인 중 오류: {e}")
        count_before = 0
    print()
    
    # 추천 도서 수집 및 저장
    result = sync_childbook_recommendations()
    
    print()
    print("=" * 60)
    print(f"수집 및 저장 완료!")
    print(f"수집된 도서 수: {result.get('count', 0)}권")
    print("=" * 60)
    
    # 저장 후 데이터 수 확인
    try:
        updated = supabase.table("childbook_items").select("*", count="exact").execute()
        count_after = updated.count if hasattr(updated, 'count') else len(updated.data) if updated.data else 0
        print(f"\n저장 후 childbook_items에 저장된 도서 수: {count_after}권")
        print(f"추가된 도서 수: {count_after - count_before}권")
        
        # 샘플 데이터 확인
        sample = supabase.table("childbook_items").select("*").limit(5).execute()
        if sample.data:
            print(f"\n샘플 데이터 (최근 5개):")
            for i, book in enumerate(sample.data[:5], 1):
                print(f"{i}. {book.get('title', 'N/A')} - {book.get('author', 'N/A')}")
    except Exception as e:
        print(f"\n저장 후 데이터 확인 중 오류: {e}")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()








