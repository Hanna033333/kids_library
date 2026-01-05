
import asyncio
import aiohttp
import time
from supabase_client import supabase

# API_URL = "http://127.0.0.1:8000" 
API_URL = "https://kids-library-7gj8.onrender.com"

async def test_prod_loan_status():
    print("1. Fetching 24 books with ISBNs from DB...")
    response = supabase.table("childbook_items") \
        .select("id, isbn") \
        .not_.is_("isbn", "null") \
        .neq("isbn", "") \
        .limit(24) \
        .execute()
    
    books = response.data
    if not books:
        print("No books found.")
        return
        
    book_ids = [b['id'] for b in books]
    print(f"Fetched {len(book_ids)} IDs.")

    # Chunking Simulation (Frontend behavior)
    chunk_size = 6
    chunks = [book_ids[i:i + chunk_size] for i in range(0, len(book_ids), chunk_size)]
    print(f"Split into {len(chunks)} chunks of {chunk_size}.")

    async with aiohttp.ClientSession() as session:
        tasks = []
        print("\n2. Sending concurrent requests...")
        start_time = time.time()
        
        for i, chunk in enumerate(chunks):
            task = fetch_chunk(session, chunk, i)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks)
        
        total_duration = time.time() - start_time
        print(f"\nTotal Duration: {total_duration:.2f}s")

async def fetch_chunk(session, chunk, index):
    url = f"{API_URL}/api/books/loan-status"
    start = time.time()
    try:
        async with session.post(url, json=chunk) as resp:
            data = await resp.json()
            duration = time.time() - start
            print(f"Chunk {index} finished in {duration:.2f}s. Status: {resp.status}")
            return data
    except Exception as e:
        print(f"Chunk {index} failed: {e}")
        return {}

if __name__ == "__main__":
    asyncio.run(test_prod_loan_status())
