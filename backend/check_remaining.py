
from supabase_client import supabase

def check_remaining():
    # Count IS NULL
    res_null = supabase.table("childbook_items") \
        .select("*", count="exact", head=True) \
        .is_("web_scraped_callno", "null") \
        .execute()
        
    print(f"Books with web_scraped_callno IS NULL: {res_null.count}")

    # Count IS NOT NULL (Done)
    res_done = supabase.table("childbook_items") \
        .select("*", count="exact", head=True) \
        .not_.is_("web_scraped_callno", "null") \
        .execute()
        
    print(f"Books with web_scraped_callno DONE: {res_done.count}")
    
    # Check if any are empty string
    res_empty = supabase.table("childbook_items") \
        .select("*", count="exact", head=True) \
        .eq("web_scraped_callno", "") \
        .execute()
        
    print(f"Books with web_scraped_callno = '': {res_empty.count}")

if __name__ == "__main__":
    check_remaining()
