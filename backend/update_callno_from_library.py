#!/usr/bin/env python
"""
Update childbook_items pangyo_callno from library_items based on ISBN match
"""

from supabase_client import supabase

def update_callno_from_library():
    
    # First, check the structure of both tables
    print("Checking library_items table...")
    lib_sample = supabase.table("library_items").select("*").limit(5).execute()
    print(f"Library items sample (first 5):")
    for item in lib_sample.data:
        print(f"  ISBN: {item.get('isbn')}, Callno: {item.get('pangyo_callno')}")
    
    print("\nChecking childbook_items table...")
    child_sample = supabase.table("childbook_items").select("*").limit(5).execute()
    print(f"Childbook items sample (first 5):")
    for item in child_sample.data:
        print(f"  ISBN: {item.get('isbn')}, Callno: {item.get('pangyo_callno')}")
    
    # Get all items from library_items
    print("\nFetching all library_items...")
    library_items = supabase.table("library_items").select("isbn, pangyo_callno").execute()
    
    # Create a mapping of ISBN -> callno
    isbn_to_callno = {}
    for item in library_items.data:
        isbn = item.get('isbn')
        callno = item.get('pangyo_callno')
        if isbn and callno:
            isbn_to_callno[isbn] = callno
    
    print(f"Found {len(isbn_to_callno)} library items with ISBN and callno")
    
    # Get all childbook_items
    print("Fetching all childbook_items...")
    childbook_items = supabase.table("childbook_items").select("id, isbn, pangyo_callno").execute()
    
    # Update childbook_items with matching ISBNs
    updated_count = 0
    not_found_count = 0
    
    for item in childbook_items.data:
        isbn = item.get('isbn')
        current_callno = item.get('pangyo_callno')
        
        if isbn in isbn_to_callno:
            new_callno = isbn_to_callno[isbn]
            if current_callno != new_callno:
                print(f"Updating ID {item['id']}: {current_callno} -> {new_callno}")
                supabase.table("childbook_items").update({"pangyo_callno": new_callno}).eq("id", item['id']).execute()
                updated_count += 1
        else:
            not_found_count += 1
    
    print(f"\nUpdate complete!")
    print(f"  Updated: {updated_count}")
    print(f"  Not found in library_items: {not_found_count}")
    print(f"  Total childbook_items: {len(childbook_items.data)}")

if __name__ == "__main__":
    update_callno_from_library()
