#!/usr/bin/env python
"""
Test API and save full response
"""

import requests
import json
from core.config import DATA4LIBRARY_KEY

test_isbn = "9791185934945"
url = "http://data4library.kr/api/libSrchByBook"

# 경기도로 테스트
params = {
    "authKey": DATA4LIBRARY_KEY,
    "isbn": test_isbn,
    "region": "31",  # 경기도
    "pageNo": 1,
    "pageSize": 100,
    "format": "json"
}

print(f"Testing API with region=31 (경기도)...")
response = requests.get(url, params=params, timeout=10)
data = response.json()

# Save full response
with open("api_response_full.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Response saved to api_response_full.json")
print(f"NumFound: {data.get('response', {}).get('numFound')}")

# Look for Pangyo library
libs = data.get("response", {}).get("libs", [])
print(f"Libraries found: {len(libs)}")

pangyo_lib_code = "141231"
for lib_data in libs:
    lib = lib_data.get("lib", {})
    if lib.get("libCode") == pangyo_lib_code or "판교" in lib.get("libName", ""):
        print(f"\n✅ Found Pangyo library!")
        print(f"  Name: {lib.get('libName')}")
        print(f"  Code: {lib.get('libCode')}")
        
        # Check for book data
        book = lib_data.get("book", {})
        if book:
            print(f"  Book data:")
            print(f"    - vol: {book.get('vol')}")
            print(f"    - class_no: {book.get('class_no')}")
            print(f"    - loanCnt: {book.get('loan_cnt')}")
