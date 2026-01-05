
from supabase_client import supabase
from datetime import datetime, timedelta

def check_recent_inserts():
    print("Checking for recently added books...")
    
    # 1. Exact Count
    count_res = supabase.table("childbook_items").select("*", count="exact", head=True).execute()
    total_count = count_res.count
    print(f"Total Exact Count: {total_count}")
    
    # 2. Created today (approx)
    # Get current time in UTC/ISO
    # Assuming KST is used by user, but DB is UTC (usually).
    # If DB created_at is timestamptz.
    
    # Let's check last 24 hours.
    one_day_ago = (datetime.utcnow() - timedelta(days=1)).isoformat()
    
    recent_res = supabase.table("childbook_items") \
        .select("id, title, created_at") \
        .gt("created_at", one_day_ago) \
        .execute()
        
    recent_books = recent_res.data
    print(f"Books added in last 24h: {len(recent_books)}")
    
    if recent_books:
        print("Examples:")
        for b in recent_books[:5]:
            print(f"- {b['title']} ({b['created_at']})")
            
if __name__ == "__main__":
    check_recent_inserts()
