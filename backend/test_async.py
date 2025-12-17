#!/usr/bin/env python
"""
Quick test of async function
"""

import asyncio
import aiohttp
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"

async def test():
    test_isbn = "9791141611422"
    
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "TITLE",
        "keyword": "별별수사대",
        "pageNo": 1,
        "pageSize": 100,
        "format": "json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=10) as response:
            data = await response.json()
            
            print(f"Status Code: {response.status}")
            print(f"ISBN: {test_isbn}")
            
            response_data = data.get("response", {})
            docs = response_data.get("docs", [])
            
            print(f"Docs found: {len(docs)}")
            
            for doc_wrapper in docs:
                doc = doc_wrapper.get("doc", {})
                print(f"  - Title: {doc.get('bookname')}")
                print(f"    ISBN: {doc.get('isbn13')}")
                print(f"    vol: {doc.get('vol')}")
                print(f"    class_no: {doc.get('class_no')}")

if __name__ == "__main__":
    asyncio.run(test())
