#!/usr/bin/env python
"""
Test itemSrch pagination and max pageSize
"""
import requests
import json
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"

def test_page(page, size):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "ALL",
        "pageNo": page,
        "pageSize": size,
        "format": "json"
    }
    
    print(f"Fetching page {page} with size {size}...")
    try:
        r = requests.get(url, params=params, timeout=20)
        d = r.json()
        num = d["response"]["numFound"]
        docs = d["response"]["docs"]
        print(f"NumFound: {num}")
        print(f"Docs returned: {len(docs)}")
        if docs:
            print(f"First doc: {docs[0]['doc']['bookname']}")
    except Exception as e:
        print(f"Error: {e}")

test_page(1, 1000)
