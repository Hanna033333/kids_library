#!/usr/bin/env python
import requests
from core.config import DATA4LIBRARY_KEY

KNOWN_ISBN = "9791130663074"
PANGYO_LIB_CODE = "141231"

def test_endpoint(endpoint):
    url = f"http://data4library.kr/api/{endpoint}"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "isbn": KNOWN_ISBN,
        "format": "json"
    }
    
    print(f"Testing {endpoint}...")
    try:
        r = requests.get(url, params=params, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 30)

test_endpoint("srchBooks")
test_endpoint("bookExist")
test_endpoint("search/book")
