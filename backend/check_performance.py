import time
import sys
from core.database import supabase

def check_perms():
    print("Benchmarking queries on childbook_items...", flush=True)
    
    # Test 1: Simple Pagination (No Sort)
    start = time.time()
    try:
        res = supabase.table("childbook_items").select("*").limit(20).execute()
        duration = time.time() - start
        print(f"1. Simple Usage (Limit 20): {duration:.4f}s", flush=True)
    except Exception as e:
        print(f"1. Failed: {e}", flush=True)
    
    # Test 2: Sort by pangyo_callno (Target Index)
    start = time.time()
    try:
        res = supabase.table("childbook_items").select("*").order("pangyo_callno").limit(20).execute()
        duration = time.time() - start
        print(f"2. Sort by pangyo_callno: {duration:.4f}s", flush=True)
    except Exception as e:
        print(f"2. Failed: {e}", flush=True)
    
    # Test 3: Search Title
    start = time.time()
    try:
        res = supabase.table("childbook_items").select("*").ilike("title", "%고양이%").limit(20).execute()
        duration = time.time() - start
        print(f"3. Search Title (ilike '고양이'): {duration:.4f}s", flush=True)
    except Exception as e:
        print(f"3. Failed: {e}", flush=True)

if __name__ == "__main__":
    check_perms()
