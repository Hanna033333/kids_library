import requests
from core.config import DATA4LIBRARY_KEY

def test_itemsrch_isbn(isbn):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "type": "ISBN",
        "keyword": isbn,
        "format": "json"
    }
    
    print(f"\n--- Testing itemSrch for ISBN: {isbn} ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        response_data = data.get("response", {})
        num_found = response_data.get("numFound", 0)
        print(f"Num Found: {num_found}")
        
        docs = response_data.get("docs", [])
        for i, doc_wrapper in enumerate(docs):
            doc = doc_wrapper.get("doc", {})
            print(f"[{i+1}] Title: {doc.get('bookname')}, ISBN: {doc.get('isbn13')}, Vol: {doc.get('vol')}")
            
        if not docs:
            print("No results found.")
            err = response_data.get("error")
            if err: print(f"API Error: {err}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test some ISBNs from the failing list
    test_itemsrch_isbn("9788949113760") # 안녕, 나의 등대
    test_itemsrch_isbn("9788949111131") # 고양이 폭풍
