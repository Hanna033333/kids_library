import requests
import os
from core.config import ALADIN_TTB_KEY

def search_aladin(title, author="", publisher=""):
    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    query = f"{title} {author} {publisher}".strip()
    params = {
        "ttbkey": ALADIN_TTB_KEY,
        "Query": query,
        "QueryType": "Keyword",
        "MaxResults": 5,
        "start": 1,
        "SearchTarget": "Book",
        "output": "js",
        "Version": "20131101"
    }
    
    print(f"Searching Aladin for: '{query}'")
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("item", [])
            print(f"Found {len(items)} items.")
            for i, item in enumerate(items):
                print(f"Result {i+1}:")
                print(f"  Title: {item.get('title')}")
                print(f"  Author: {item.get('author')}")
                print(f"  Publisher: {item.get('publisher')}")
                print(f"  ISBN13: {item.get('isbn13')}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_aladin("금방울전")
