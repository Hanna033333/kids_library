import requests
from core.config import DATA4LIBRARY_KEY

def test_itemsrch_callno(callno):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "type": "callNumber",
        "keyword": callno,
        "format": "json"
    }
    
    print(f"\n--- Testing itemSrch for Call Number: {callno} ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        response_data = data.get("response", {})
        num_found = response_data.get("numFound", 0)
        print(f"Num Found: {num_found}")
        
        docs = response_data.get("docs", [])
        for i, doc_wrapper in enumerate(docs[:5]):
            doc = doc_wrapper.get("doc", {})
            print(f"[{i+1}] Title: {doc.get('bookname')}, ISBN: {doc.get('isbn13')}, Vol: {doc.get('vol')}")
            
        if not docs:
            print("No results found.")
            err = response_data.get("error")
            if err: print(f"API Error: {err}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test one of the failing call numbers
    test_itemsrch_callno("유 808.9-ㅂ966ㅂ")
    test_itemsrch_callno("아 808.9-ㅅ812")
