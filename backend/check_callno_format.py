"""
수집된 데이터에서 청구기호 형식 확인
"""
from supabase_client import supabase

print("=" * 60)
print("수집된 library_items 데이터의 청구기호 형식 확인")
print("=" * 60)
print()

# '밤마다 환상축제' 책 찾기
result = supabase.table("library_items").select("*").ilike("title", "%밤마다%").execute()

if result.data:
    print(f"✅ '밤마다 환상축제' 책 찾음: {len(result.data)}건")
    print()
    for book in result.data:
        print(f"제목: {book.get('title', 'N/A')}")
        print(f"청구기호: {book.get('callno', 'N/A')}")
        print(f"ISBN: {book.get('isbn13', 'N/A')}")
        print()
else:
    print("❌ '밤마다 환상축제' 책을 찾을 수 없습니다.")
    print()
    print("대신 최근 수집된 데이터 확인:")
    print("-" * 60)
    
    # 최근 데이터 확인
    recent = supabase.table("library_items").select("*").limit(10).execute()
    for i, book in enumerate(recent.data[:5], 1):
        print(f"{i}. {book.get('title', 'N/A')[:50]}")
        print(f"   청구기호: {book.get('callno', 'N/A')}")
        print()






