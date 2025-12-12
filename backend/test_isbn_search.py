"""
ISBN 검색 테스트 (실제 데이터 샘플)
"""
from supabase_client import supabase
from library_api import search_isbn
import json

# ISBN이 없는 항목 5개 가져오기
items = supabase.table("childbook_items").select("id,title,author,isbn").is_("isbn", "null").limit(5).execute()

print("=" * 60)
print("ISBN 검색 테스트 (실제 데이터 샘플)")
print("=" * 60)
print()

for item in items.data:
    item_id = item.get("id")
    title = item.get("title", "").strip()
    author_raw = item.get("author", "").strip()
    
    print(f"ID: {item_id}")
    print(f"제목: {title}")
    print(f"저자: {author_raw}")
    
    # 저자 정보 정리
    author = None
    if author_raw:
        author_parts = author_raw.split("|")
        first_author = author_parts[0].strip()
        author_clean = first_author.replace("글", "").replace("그림", "").replace("옮김", "").replace(",", "").strip()
        if author_clean:
            author = author_clean
    
    print(f"정리된 저자: {author}")
    
    # ISBN 검색
    isbn, score = search_isbn(title, author)
    
    print(f"검색 결과 - ISBN: {isbn}, 유사도: {score}")
    print("-" * 60)
    print()


