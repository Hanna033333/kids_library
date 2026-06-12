from supabase_client import supabase
import sys

# Force UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

keywords = ["똥", "방귀", "학교", "귀신", "괴물"]

for keyword in keywords:
    print(f"\nSearching for: {keyword}")
    result = supabase.table('childbook_items').select('id, title, author, publisher').ilike('title', f'%{keyword}%').limit(10).execute()
    
    for book in result.data:
        print(f"[{book['id']}] {book['title']} / {book.get('author','')} / {book.get('publisher','')}")
