# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from supabase import create_client
import os
from dotenv import load_dotenv
import requests
import json
import time

load_dotenv()

BASE_URL = "https://kids-library-7gj8.onrender.com"

def main():
    try:
        # 1. Get Winter Book ID from DB
        print("Connecting to DB...")
        sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        res = sb.table('childbook_items').select('id, title, image_url').eq('curation_tag', '겨울방학2026').limit(1).execute()
        
        if not res.data:
            print("No winter books found in DB!")
            return
            
        book = res.data[0]
        book_id = book['id']
        print(f"Checkout Book: {book['title']} (ID: {book_id})")
        print(f"Image URL: {book['image_url']}")
        
        # 2. Call Production API
        print(f"\nChecking API: {BASE_URL}/api/books/{book_id}")
        start = time.time()
        api_res = requests.get(f"{BASE_URL}/api/books/{book_id}", timeout=15)
        duration = time.time() - start
        
        print(f"Status Code: {api_res.status_code}")
        print(f"Duration: {duration:.2f}s")
        
        if api_res.status_code == 200:
            data = api_res.json()
            print("\nAPI Response Preview:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")
            
            # Check library_info
            lib_info = data.get('library_info', [])
            print(f"\nLibrary Info Count: {len(lib_info)}")
            if lib_info:
                print(f"First Library: {lib_info[0]}")
        else:
            print(f"\nError Response: {api_res.text}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
