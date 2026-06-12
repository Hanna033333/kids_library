
import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")
if not key:
    key = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

async def compare_duplicates():
    print("Comparing duplicate records...")
    
    target_isbns = ['9788950998370', '9788958282792', '9788986621785']
    
    try:
        response = supabase.table("childbook_items").select("*").in_("isbn", target_isbns).execute()
        data = response.data
        
        # Group by ISBN
        grouped = {}
        for item in data:
            isbn = item['isbn']
            if isbn not in grouped:
                grouped[isbn] = []
            grouped[isbn].append(item)
            
        for isbn, items in grouped.items():
            print(f"\n==================================================")
            print(f"ISBN: {isbn}")
            print(f"==================================================")
            
            items.sort(key=lambda x: x['id'])
            item1 = items[0]
            item2 = items[1]
            
            print(f"{'Field':<20} | {'ID ' + str(item1['id']) + ' (OLD)':<40} | {'ID ' + str(item2['id']) + ' (NEW)':<40}")
            print("-" * 110)
            
            all_keys = set(item1.keys()) | set(item2.keys())
            
            for key in sorted(all_keys):
                val1 = str(item1.get(key, ''))
                val2 = str(item2.get(key, ''))
                
                # Truncate long values for display
                if len(val1) > 35: val1 = val1[:35] + "..."
                if len(val2) > 35: val2 = val2[:35] + "..."
                
                marker = " "
                if val1 != val2:
                    marker = "*" # Mark differences
                    
                print(f"{marker} {key:<18} | {val1:<40} | {val2:<40}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(compare_duplicates())
