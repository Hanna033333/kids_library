#!/usr/bin/env python
"""
Bulk scan Pangyo library items to find volume info for specific books
since search API is not working effectively.
"""

import asyncio
import aiohttp
from supabase_client import supabase
from core.config import DATA4LIBRARY_KEY
from collections import defaultdict
import time

PANGYO_LIB_CODE = "141231"
PAGE_SIZE = 1000  # Try to fetch max per page

def get_target_isbns():
    """
    Get list of ISBNs that need volume info
    """
    print("🔍 Fetching target ISBNs from database...")
    response = supabase.table("childbook_items").select("id, isbn, title, pangyo_callno").execute()
    books = response.data
    
    # Find duplicates
    callno_groups = defaultdict(list)
    for book in books:
        callno = book.get("pangyo_callno")
        if callno and callno.strip() and book.get("isbn"):
            callno_groups[callno].append(book)
            
    target_isbns = set()
    for callno, book_list in callno_groups.items():
        if len(book_list) > 1:
            for book in book_list:
                target_isbns.add(book['isbn'])
                
    print(f"✅ Found {len(target_isbns)} unique ISBNs to find.")
    return target_isbns

async def scan_library_items(target_isbns):
    url = "http://data4library.kr/api/itemSrch"
    found_volumes = {} # isbn -> {vol, class_no}
    
    async with aiohttp.ClientSession() as session:
        # First get total count
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": PANGYO_LIB_CODE,
            "type": "ALL",
            "pageNo": 1,
            "pageSize": 1,
            "format": "json"
        }
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            total_count = data.get("response", {}).get("numFound", 0)
            
        print(f"📚 Total items in library: {total_count}")
        total_pages = (total_count // PAGE_SIZE) + 1
        
        # Scan pages
        print(f"🚀 Scanning {total_pages} pages...")
        
        # Concurrency limit
        sem = asyncio.Semaphore(5) 
        
        async def fetch_page(page):
            async with sem:
                page_params = {
                    "authKey": DATA4LIBRARY_KEY,
                    "libCode": PANGYO_LIB_CODE,
                    "type": "ALL",
                    "pageNo": page,
                    "pageSize": PAGE_SIZE,
                    "format": "json"
                }
                try:
                    async with session.get(url, params=page_params, timeout=30) as r:
                         d = await r.json()
                         docs = d.get("response", {}).get("docs", [])
                         return docs
                except Exception as e:
                    print(f"⚠️ Page {page} failed: {e}")
                    return []

        # Process in chunks of pages to avoid OOM or flooding
        chunk_size = 20
        for i in range(1, total_pages + 1, chunk_size):
            end_page = min(i + chunk_size, total_pages + 1)
            tasks = [fetch_page(p) for p in range(i, end_page)]
            
            print(f"  Scanning pages {i} to {end_page-1}...")
            results = await asyncio.gather(*tasks)
            
            for docs in results:
                for doc_wrapper in docs:
                    doc = doc_wrapper.get("doc", {})
                    isbn = doc.get("isbn13", "")
                    if isbn in target_isbns:
                        vol = doc.get("vol", "").strip()
                        if vol:
                            found_volumes[isbn] = {
                                "vol": vol,
                                "class_no": doc.get("class_no", "")
                            }
                            print(f"    ✨ Found! ISBN {isbn} -> Vol: {vol}")
            
            # Check if we found all
            if len(found_volumes) == len(target_isbns):
                print("🎉 All targets found! Stopping early.")
                break
                
    return found_volumes

async def main():
    target_isbns = get_target_isbns()
    if not target_isbns:
        return
        
    found_data = await scan_library_items(target_isbns)
    
    print("\n" + "="*60)
    print(f"✅ Found data for {len(found_data)} / {len(target_isbns)} books")
    print("="*60)
    
    # Update DB
    print("\n🔄 Updating database...")
    for isbn, data in found_data.items():
        vol = data['vol']
        if vol:
            try:
                # Update all books with this ISBN (usually just one, but could be duplicates)
                # First get IDs
                res = supabase.table("childbook_items").select("id, title").eq("isbn", isbn).execute()
                for book in res.data:
                    supabase.table("childbook_items").update({"vol": vol}).eq("id", book['id']).execute()
                    print(f"  ✅ Updated: {book['title'][:20]}... -> vol: {vol}")
            except Exception as e:
                print(f"  ❌ Update failed for {isbn}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
