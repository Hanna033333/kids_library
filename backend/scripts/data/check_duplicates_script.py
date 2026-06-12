
import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY") # Use service key for admin tasks if available, or ANON
if not key:
    key = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

async def check_duplicates():
    print("Checking for duplicate ISBNs...")
    
    # This might be heavy if table is huge, but for "childbook_items" it should be fine.
    # We'll fetch all ISBNs and IDs.
    try:
        response = supabase.table("childbook_items").select("id, isbn, title, created_at").execute()
        data = response.data
        
        isbn_map = {}
        duplicates = []
        
        for item in data:
            isbn = item.get('isbn')
            if not isbn:
                continue
                
            if isbn in isbn_map:
                duplicates.append(item)
                isbn_map[isbn].append(item)
            else:
                isbn_map[isbn] = [item]
                
        actual_duplicates = {k: v for k, v in isbn_map.items() if len(v) > 1}
        
        if not actual_duplicates:
            print("No duplicate ISBNs found.")
        else:
            print(f"Found {len(actual_duplicates)} ISBNs with duplicates:")
            for isbn, items in actual_duplicates.items():
                print(f"\nISBN: {isbn}")
                # Sort by ID to show which one would be kept
                items.sort(key=lambda x: x['id'])
                for i, item in enumerate(items):
                    action = "KEEP (Latest)" if i == len(items) - 1 else "DELETE"
                    print(f"  - [{action}] ID: {item['id']}, Title: {item['title']}, Created: {item.get('created_at')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_duplicates())
