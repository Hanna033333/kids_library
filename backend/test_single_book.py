#!/usr/bin/env python
"""
Test single book to see full API response
"""

import requests
import json
from core.config import DATA4LIBRARY_KEY

# 중복 청구기호 중 첫 번째 ISBN 테스트
test_isbn = "9791185934945"  # 문제아 / 아 813.8-ㄱ985ㄴ

url = "http://data4library.kr/api/libSrchByBook"
params = {
    "authKey": DATA4LIBRARY_KEY,
    "isbn": test_isbn,
    "region": "31",  # 경기도
    "pageNo": 1,
    "pageSize": 100,
    "format": "json"
}

print(f"Testing ISBN: {test_isbn}")
print(f"URL: {url}")
print()

response = requests.get(url, params=params, timeout=10)
data = response.json()

# Save for inspection
with open("single_book_test.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Response saved to single_book_test.json")
print()

# Parse response
response_data = data.get("response", {})
libs = response_data.get("libs", [])

print(f"Total libraries found: {len(libs)}")
print()

# Find Pangyo library
PANGYO_LIB_CODE = "141231"
for lib_data in libs:
    lib = lib_data.get("lib", {})
    lib_code = lib.get("libCode")
    lib_name = lib.get("libName")
    
    if lib_code == PANGYO_LIB_CODE or "판교" in lib_name:
        print(f"✅ Found Pangyo Library!")
        print(f"   Name: {lib_name}")
        print(f"   Code: {lib_code}")
        
        # Check book data
        book_data = lib_data.get("book")
        if book_data:
            if isinstance(book_data, list):
                print(f"   Books: {len(book_data)}")
                for book in book_data[:3]:
                    print(f"      - vol: {book.get('vol')}")
                    print(f"        class_no: {book.get('class_no')}")
            else:
                print(f"   Book (single):")
                print(f"      - vol: {book_data.get('vol')}")
                print(f"      - class_no: {book_data.get('class_no')}")
        else:
            print("   ❌ No book data!")
        print()

if not any(lib.get("libCode") == PANGYO_LIB_CODE for lib_data in libs for lib in [lib_data.get("lib", {})]):
    print("❌ Pangyo library NOT found in results!")
    print("First 3 libraries:")
    for lib_data in libs[:3]:
        lib = lib_data.get("lib", {})
        print(f"   - {lib.get('libName')} ({lib.get('libCode')})")
