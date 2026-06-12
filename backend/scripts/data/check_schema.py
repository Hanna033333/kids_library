
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

async def check_columns():
    print("Checking columns...")
    try:
        # Fetch one row to see keys
        response = supabase.table("childbook_items").select("*").limit(1).execute()
        if response.data:
            print("Columns found:", list(response.data[0].keys()))
        else:
            print("No data found, cannot infer columns from row.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_columns())
