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

def hide_books_without_callno():
    print("Hiding books without valid call numbers...")

    # update 1: pangyo_callno is NULL
    data, count = supabase.table('childbook_items') \
        .update({'is_hidden': True}) \
        .is_('pangyo_callno', 'null') \
        .execute()
    
    print(f"Updated (NULL): {len(data[1])} rows")

    # update 2: pangyo_callno is empty string
    data, count = supabase.table('childbook_items') \
        .update({'is_hidden': True}) \
        .eq('pangyo_callno', '') \
        .execute()
    
    print(f"Updated (Empty): {len(data[1])} rows")

    # update 3: pangyo_callno is '없음'
    data, count = supabase.table('childbook_items') \
        .update({'is_hidden': True}) \
        .eq('pangyo_callno', '없음') \
        .execute()
        
    print(f"Updated ('없음'): {len(data[1])} rows")

    # update 4: pangyo_callno is '청구기호 없음'
    data, count = supabase.table('childbook_items') \
        .update({'is_hidden': True}) \
        .eq('pangyo_callno', '청구기호 없음') \
        .execute()
        
    print(f"Updated ('청구기호 없음'): {len(data[1])} rows")

if __name__ == "__main__":
    hide_books_without_callno()
