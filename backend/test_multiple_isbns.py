#!/usr/bin/env python
"""
Test multiple ISBNs to find one that Pangyo library has
"""

import requests
import json
from core.config import DATA4LIBRARY_KEY
from supabase_client import supabase

# Get duplicate callnos
response = supabase.table("childbook_items").select("isbn, title, pangyo_callno").execute()
books = response.data

# Find books with duplicate callnos
from collections import defaultdict
callno_groups = defaultdict(list)
for book in books:
    callno = book.get("pangyo_callno")
    if callno and callno.strip() and book.get("isbn"):
        callno_groups[callno].append(book)

duplicates = {callno: books for callno, books in callno_groups.items() if len(books) > 1}

print(f"Found {len(duplicates)} duplicate callnos")
print()

# Test first 5 ISBNs
PANGYO_LIB_CODE = "141231"
url = "http://data4library.kr/api/libSrchByBook"

test_count = 0
found_pangyo = False

for callno, books_list in list(duplicates.items())[:5]:
    for book in books_list[:1]:  # Test first book of each callno
        isbn = book.get("isbn")
        if not isbn:
            continue
            
        test_count += 1
        print(f"Test {test_count}: {book.get('title')[:30]}")
        print(f"   ISBN: {isbn}")
        print(f"   Callno: {callno}")
        
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "isbn": isbn,
            "region": "31",
            "pageNo": 1,
            "pageSize": 200,  # Increase page size
            "format": "json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            libs = data.get("response", {}).get("libs", [])
            
            # Check for Pangyo
            for lib_data in libs:
                lib = lib_data.get("lib", {})
                if lib.get("libCode") == PANGYO_LIB_CODE:
                    print(f"   ✅ PANGYO FOUND!")
                    book_data = lib_data.get("book")
                    if book_data:
                        if not isinstance(book_data, list):
                            book_data = [book_data]
                        for b in book_data:
                            print(f"      vol: {b.get('vol')}")
                            print(f"      class_no: {b.get('class_no')}")
                    found_pangyo = True
                    break
            
            if not found_pangyo:
                print(f"   ❌ Pangyo not found ({len(libs)} libs)")
        except Exception as e:
            print(f"   Error: {e}")
        
        print()
        
        if test_count >= 10:
            break
    
    if test_count >= 10:
        break

if not found_pangyo:
    print("\n⚠️  판교 도서관이 이 ISBN들을 소장하지 않는 것 같습니다!")
    print("   다른 방법을 시도해야 할 수 있습니다.")
