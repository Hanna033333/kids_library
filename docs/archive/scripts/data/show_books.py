from supabase_client import supabase

result = supabase.table('childbook_items').select('title,author,publisher').eq('curation_tag','겨울방학2026').limit(5).execute()

for book in result.data:
    print(f"{book['title']} / {book.get('author','')} / {book.get('publisher','')}")
