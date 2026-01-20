import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', '.env.local')
load_dotenv(dotenv_path)

url: str = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key: str = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

def force_hide_books():
    print("Force hiding books 11300 and 11303...")
    
    # Force update by ID
    data, count = supabase.table('childbook_items') \
        .update({'is_hidden': True}) \
        .in_('id', [11300, 11303]) \
        .execute()
    
    print(f"Force Updated: {len(data[1])} rows")
    print(data[1])

if __name__ == "__main__":
    force_hide_books()
