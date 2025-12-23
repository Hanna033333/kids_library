import requests
import json
from core.config import DATA4LIBRARY_KEY

def test_title_search(title):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "type": "TITLE",
        "keyword": title,
        "format": "json"
    }
    
    print(f"\n--- Testing Title Search: '{title}' ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        num_found = data.get("response", {}).get("numFound", 0)
        print(f"NumFound: {num_found}")
        
        if num_found > 0:
            docs = data.get("response", {}).get("docs", [])
            print(f"Showing first {len(docs)} results:")
            for i, d in enumerate(docs):
                doc = d.get("doc", {})
                print(f"  [{i+1}] {doc.get('bookname')} | {doc.get('authors')}")
        else:
            print("No results found.")
            err = data.get("response", {}).get("error")
            if err: print(f"API Error: {err}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_title_search("검은 새")
    test_title_search("오즈의 마법사")
