import requests
from core.config import DATA4LIBRARY_KEY

def test_global_search(title):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "type": "title",
        "keyword": title,
        "format": "json",
        "pageSize": 5
    }
    
    print(f"\n--- Testing Global Title Search (No libCode): '{title}' ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        num_found = data.get("response", {}).get("numFound", 0)
        print(f"NumFound globally: {num_found}")
        
        if 0 < num_found < 1000000: # Global search should return some results
            docs = data.get("response", {}).get("docs", [])
            for i, d in enumerate(docs):
                doc = d.get("doc", {})
                print(f"  [{i+1}] {doc.get('bookname')} | {doc.get('authors')}")
        else:
            print("Still getting a massive/unfiltered number of results.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_global_search("검은 새")
