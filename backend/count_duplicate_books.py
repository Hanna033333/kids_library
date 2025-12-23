
from supabase_client import supabase
from collections import defaultdict

def count_duplicates():
    response = supabase.table("childbook_items").select("id, pangyo_callno").execute()
    books = response.data
    
    callno_groups = defaultdict(list)
    for book in books:
        callno = book.get("pangyo_callno")
        if callno and callno.strip():
            callno_groups[callno].append(book)
    
    duplicates = {
        callno: books_list 
        for callno, books_list in callno_groups.items() 
        if len(books_list) > 1
    }
    
    total_books = sum(len(books) for books in duplicates.values())
    print(f"Groups: {len(duplicates)}")
    print(f"Total books: {total_books}")

if __name__ == "__main__":
    count_duplicates()
