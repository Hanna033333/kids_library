
import asyncio
from supabase_client import supabase

async def count_scraped():
    # Count how many have web_scraped_callno populated
    # We check for not null and not empty string (if applicable)
    # Actually just not null is enough based on script logic
    res = supabase.table("childbook_items") \
        .select("id", count="exact") \
        .not_.is_("web_scraped_callno", "null") \
        .execute()
    
    print(f"Total scraped in DB: {res.count}")

if __name__ == "__main__":
    asyncio.run(count_scraped())
