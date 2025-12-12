"""
단일 책으로 청구기호 테스트
"""
from main import sync_library_books_child
from supabase_client import supabase

print("=" * 60)
print("'밤마다 환상축제' 책의 청구기호 확인")
print("=" * 60)
print()

# 짧은 기간으로 테스트 (해당 책이 포함된 기간)
result = sync_library_books_child('2024-12-01', '2024-12-31')

print()
print("=" * 60)
print(f"수집 완료: {result.get('count', 0)}권")
print("=" * 60)
print()

# '밤마다 환상축제' 책 찾기
book_result = supabase.table("library_items").select("*").ilike("title", "%밤마다%").execute()

if book_result.data:
    for book in book_result.data:
        print(f"✅ 책 찾음: {book.get('title', 'N/A')}")
        print(f"   청구기호: {book.get('callno', 'N/A')}")
        print(f"   ISBN: {book.get('isbn13', 'N/A')}")
else:
    print("❌ '밤마다 환상축제' 책을 찾을 수 없습니다.")






