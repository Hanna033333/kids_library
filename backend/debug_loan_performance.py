import asyncio
import time
from services.loan_status import fetch_loan_status_batch
from core.database import supabase
import aiohttp

async def run_test():
    print("1. Fetching 24 books with ISBNs from DB...")
    # Get 24 random books with ISBN
    response = supabase.table("childbook_items") \
        .select("id, isbn, title") \
        .not_.is_("isbn", "null") \
        .neq("isbn", "") \
        .limit(24) \
        .execute()
    
    books = response.data
    print(f"Fetched {len(books)} books.")
    
    if not books:
        print("No books found.")
        return

    print("\n2. Calling fetch_loan_status_batch (Simulating one batch)...")
    start_time = time.time()
    
    results = await fetch_loan_status_batch(books)
    
    duration = time.time() - start_time
    print(f"\nCompleted in {duration:.2f} seconds.")
    print(f"Results count: {len(results)}")
    
    success_count = 0
    error_count = 0
    unknown_count = 0
    
    print("\n--- Detailed Results ---")
    for book_id, res in results.items():
        status = res.get('status')
        if status == '확인불가':
            error_count += 1
            print(f"ID {book_id}: Error - {res.get('error')}")
        elif status == '정보없음':
            unknown_count += 1
        else:
            success_count += 1
            # print(f"ID {book_id}: {status}")
            
    print("-" * 30)
    print(f"Success: {success_count}")
    print(f"Error: {error_count}")
    print(f"Unknown: {unknown_count}")
    print(f"Total Time: {duration:.2f}s")
    
    if duration > 10:
        print("\n⚠️ WARNING: Performance is SLOW (> 10s).")
    else:
        print("\n✅ Performance is ACCEPTABLE (< 10s).")

if __name__ == "__main__":
    asyncio.run(run_test())
