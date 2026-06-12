import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', '.env.local')
load_dotenv(dotenv_path)

url: str = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key: str = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url:
    print("Error: NEXT_PUBLIC_SUPABASE_URL not found")
if not key:
    print("Error: NEXT_PUBLIC_SUPABASE_ANON_KEY not found")

supabase: Client = create_client(url, key)

def inspect_books():
    print("Inspecting books 11300 and 11303...")
    response = supabase.table('childbook_items') \
        .select('id, title, pangyo_callno, is_hidden') \
        .in_('id', [11300, 11303]) \
        .execute()
    
    print(response.data)

if __name__ == "__main__":
    inspect_books()
