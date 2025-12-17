#!/usr/bin/env python
import requests
import json
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"
KNOWN_ISBN = "9791130663074"
KNOWN_TITLE = "약이 되는 세월"

def test(params):
    url = "http://data4library.kr/api/srchBooks"
    base = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "format": "json"
    }
    base.update(params)
    
    print(f"Params: {params}")
    r = requests.get(url, params=base, timeout=10)
    try:
        d = r.json()
        print(json.dumps(d, indent=2, ensure_ascii=False)[:500])
    except:
        print(r.text[:500])
    print("-" * 40)

# Test with ISBN
test({"isbn": KNOWN_ISBN})
# Test with Title
test({"title": KNOWN_TITLE})
# Test with keyword (common)
test({"keyword": KNOWN_TITLE})
