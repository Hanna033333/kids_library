import os
import sys

# Add current directory to path to allow imports
sys.path.append(os.getcwd())

from core.database import supabase

def get_missing_samples():
    print("Fetching books with '없음' call number (Batch 2)...")
    
    # Fetch 5 random books with '없음' (offset 10 to avoid previous ones)
    response = supabase.table("childbook_items") \
        .select("id, title, isbn, pangyo_callno") \
        .eq("pangyo_callno", "없음") \
        .range(10, 14) \
        .execute()
        
    books = response.data
    
    print(f"Found {len(books)} samples:")
    for book in books:
        print("-" * 20)
        print(f"ID: {book['id']}")
        print(f"Title: {book['title']}")
        print(f"ISBN: {book['isbn']}")
        print(f"CallNo: {book['pangyo_callno']}")

if __name__ == "__main__":
    get_missing_samples()
