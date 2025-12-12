"""
현재 수집 진행 상황 확인
"""
from supabase_client import supabase
from crawler import DATA4LIBRARY_KEY, PANGYO_CODE
import requests

print("=" * 60)
print("현재 수집 진행 상황 확인")
print("=" * 60)
print()

# 1. 현재 저장된 데이터 수
try:
    result = supabase.table("library_items").select("*", count="exact").execute()
    total_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
    print(f"✅ 현재 저장된 도서 수: {total_count:,}권")
except Exception as e:
    print(f"❌ 데이터 확인 중 오류: {e}")
    total_count = 0

print()

# 2. 최근 수집된 도서 샘플 확인
try:
    recent_books = supabase.table("library_items").select("*").limit(5).execute()
    if recent_books.data:
        print("최근 저장된 도서 샘플:")
        print("-" * 60)
        for i, book in enumerate(recent_books.data[:5], 1):
            print(f"{i}. {book.get('title', 'N/A')}")
            print(f"   저자: {book.get('author', 'N/A')}")
            print(f"   청구기호: {book.get('callno', 'N/A')}")
            print()
except Exception as e:
    print(f"최근 도서 확인 중 오류: {e}")

print()
print("=" * 60)

# 3. 어제까지의 진행 상황과 비교
print("어제까지 진행 상황:")
print("-" * 60)
print("어제 완료: 459페이지, 15,525권")
print(f"현재 저장: {total_count:,}권")
print(f"차이: {total_count - 15525:,}권")
print()

if total_count > 15525:
    print(f"✅ 오늘 추가로 {total_count - 15525:,}권이 수집되었습니다!")
elif total_count == 15525:
    print("⚠️  아직 수집이 시작되지 않았거나 진행 중입니다.")
else:
    print("⚠️  데이터가 감소했습니다. 확인이 필요합니다.")

print("=" * 60)




