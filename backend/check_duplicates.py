
from supabase_client import supabase

def check_duplicates():
    print("Checking for duplicate books (title/author)...")
    
    # 1. Get all books
    res = supabase.table("childbook_items") \
        .select("id, title, author, isbn") \
        .execute()
        
    books = res.data
    print(f"Total items in DB: {len(books)}")
    
    # 2. Count by title+author
    counts = {}
    for b in books:
        key = (b['title'], b['author'])
        if key not in counts:
            counts[key] = []
        counts[key].append(b)
        
    duplicates = {k: v for k, v in counts.items() if len(v) > 1}
    
    print(f"Found {len(duplicates)} sets of duplicates.")
    
    if duplicates:
        print("\nExamples of duplicates:")
        for k, v in list(duplicates.items())[:5]:
            print(f"Title: {k[0]}")
            for item in v:
                print(f" - ID: {item['id']}, ISBN: {item['isbn']}")
            print("---")
            
if __name__ == "__main__":
    check_duplicates()
