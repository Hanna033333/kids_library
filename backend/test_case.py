#!/usr/bin/env python
from core.config import DATA4LIBRARY_KEY
import requests

KNOWN_ISBN = "9791130663074"
PANGYO_LIB_CODE = "141231"

def test_param(variation_name, params):
    url = "http://data4library.kr/api/itemSrch"
    base = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "format": "json"
    }
    base.update(params)
    try:
        r = requests.get(url, params=base, timeout=5)
        d = r.json()
        num = d["response"]["numFound"]
        print(f"[{variation_name}] NumFound: {num}")
    except Exception as e:
        print(f"[{variation_name}] Error: {e}")
        if 'd' in locals():
            print(f"Response: {d}")

print("Start...")
test_param("type=isbn", {"type": "isbn", "keyword": KNOWN_ISBN})
test_param("type=ISBN", {"type": "ISBN", "keyword": KNOWN_ISBN})
test_param("type=ALL, k_isbn", {"type": "ALL", "k_isbn": KNOWN_ISBN})
test_param("type=ALL, isbn", {"type": "ALL", "isbn": KNOWN_ISBN})
test_param("type=ALL, isbn13", {"type": "ALL", "isbn13": KNOWN_ISBN})
# Some obscure params from similar APIs
test_param("srchTarget=TOTAL", {"srchTarget": "TOTAL", "keyword": KNOWN_ISBN})
