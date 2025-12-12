from supabase_client import supabase

def upsert_book(book_data):
    return supabase.table("childbook_items").upsert(book_data).execute()
