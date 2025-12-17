#!/usr/bin/env python
"""
Test various parameters for itemSrch
"""

import requests
import json
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"
KNOWN_ISBN = "9791130663074"
KNOWN_TITLE = "약이 되는 세월"

def test_param(name, params):
    url = "http://data4library.kr/api/itemSrch"
    base_params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "format": "json"
    }
    base_params.update(params)
    
    try:
        response = requests.get(url, params=base_params, timeout=5)
        data = response.json()
        num_found = data.get("response", {}).get("numFound", 0)
        docs = data.get("response", {}).get("docs", [])
        
        result = f"[{name}] Params: {params}\n  -> NumFound: {num_found}\n"
        if docs:
            result += f"  -> First Title: {docs[0]['doc'].get('bookname')}\n"
        result += "-" * 40 + "\n"
        return result
    except Exception as e:
        return f"[{name}] Error: {e}\n" + "-" * 40 + "\n"

def main():
    output = "Testing itemSrch parameter variations...\n\n"
    
    # Variation 1: isbn13
    output += test_param("ISBN13 key", {"isbn13": KNOWN_ISBN})
    
    # Variation 2: isbn
    output += test_param("ISBN key", {"isbn": KNOWN_ISBN})
    
    # Variation 3: title
    output += test_param("Title key", {"title": KNOWN_TITLE})
    
    # Variation 4: bookname
    output += test_param("Bookname key", {"bookname": KNOWN_TITLE})
    
    # Variation 5: type=ISBN, keyword=...
    output += test_param("Type=ISBN", {"type": "ISBN", "keyword": KNOWN_ISBN})
    
    # Variation 6: type=TITLE, keyword=...
    output += test_param("Type=TITLE", {"type": "TITLE", "keyword": KNOWN_TITLE})
    
    # Variation 8: type=ALL, keyword=...
    output += test_param("Type=ALL", {"type": "ALL", "keyword": KNOWN_TITLE})

    with open("test_params_result.txt", "w", encoding="utf-8") as f:
        f.write(output)
    print("Saved to test_params_result.txt")

if __name__ == "__main__":
    main()
