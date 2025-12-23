
import requests
import json
import os
import sys
from pathlib import Path

# Add the current directory to sys.path to import core
sys.path.append(str(Path(__file__).parent))

from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"
test_callno = "유 808.9-ㅂ966ㅂ"

def test_srch_books():
    url = "http://data4library.kr/api/srchBooks"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "keyword": test_callno,
        "pageNo": 1,
        "pageSize": 100,
        "format": "json"
    }
    
    print(f"Testing srchBooks with: {test_callno}")
    response = requests.get(url, params=params)
    data = response.json()
    
    response_data = data.get("response", {})
    num_found = response_data.get("numFound", 0)
    print(f"NumFound: {num_found}")
    
    docs = response_data.get("docs", [])
    print(f"Docs returned: {len(docs)}")
    
    for i, doc_wrapper in enumerate(docs[:5]):
        doc = doc_wrapper.get("doc", {})
        print(f"[{i}] Title: {doc.get('bookname')}")
        print(f"    ISBN: {doc.get('isbn13')}")
        print(f"    Vol: {doc.get('vol')}")

if __name__ == "__main__":
    test_srch_books()
