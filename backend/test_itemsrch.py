#!/usr/bin/env python
"""
Test itemSrch API to get volume information
"""

import requests
import json
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"

# Test with a known ISBN
test_isbn = "9791141611422"  # 별별수사대
test_callno = "아 808.9-ㅂ854ㅁ"

print(f"Testing itemSrch API")
print(f"ISBN: {test_isbn}")
print(f"Callno: {test_callno}")
print()

# Try different type values
for type_val in ["ALL", "ISBN", "TITLE"]:
    print(f"\n=== Testing with type={type_val} ===")
    
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "type": type_val,
        "libCode": PANGYO_LIB_CODE,
        "authKey": DATA4LIBRARY_KEY,
        "keyword": test_isbn if type_val == "ISBN" else test_callno,
        "pageNo": 1,
        "pageSize": 10,
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        print(f"Status: {response.status_code}")
        
        # Save first response
        if type_val == "ALL":
            with open("itemsrch_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Response saved to itemsrch_response.json")
        
        # Check for results
        response_data = data.get("response", {})
        num_found = response_data.get("numFound", 0)
        result_num = response_data.get("resultNum", 0)
        
        print(f"NumFound: {num_found}")
        print(f"ResultNum: {result_num}")
        
        # Check for items
        items = response_data.get("items", [])
        if items and isinstance(items, list):
            print(f"Items found: {len(items)}")
            for item in items[:2]:
                book_data = item.get("book", {})
                print(f"  - Title: {book_data.get('bookname', 'N/A')}")
                print(f"    ISBN: {book_data.get('isbn13', 'N/A')}")
                print(f"    vol: {book_data.get('vol', 'N/A')}")
                print(f"    class_no: {book_data.get('class_no', 'N/A')}")
        else:
            print("No items found")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*60)
print("Test completed")
