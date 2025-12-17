#!/usr/bin/env python
"""
Test with a known existing ISBN from the library dump
"""

import requests
import json
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"
KNOWN_ISBN = "9791130663074"  # From itemsrch_response.json

def test(isbn):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "ISBN",
        "keyword": isbn,
        "format": "json"
    }
    
    print(f"Testing ISBN: {isbn}")
    response = requests.get(url, params=params)
    data = response.json()
    num = data.get("response", {}).get("numFound", 0)
    print(f"NumFound: {num}")

if __name__ == "__main__":
    test(KNOWN_ISBN)
