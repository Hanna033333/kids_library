import requests
from core.config import DATA4LIBRARY_KEY
from datetime import datetime

def test_itemsrch_with_dates(isbn, title):
    url = "http://data4library.kr/api/itemSrch"
    today = datetime.now().strftime("%Y-%m-%d")
    
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "type": "isbn",
        "keyword": isbn,
        "format": "json",
        "startDt": "2000-01-01",
        "endDt": today,
        "pageNo": 1,
        "pageSize": 5
    }
    
    print(f"\n--- Testing itemSrch with Date Range: {title} ({isbn}) ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        num_found = data.get("response", {}).get("numFound", 0)
        print(f"NumFound: {num_found}")
        
        if 0 < num_found < 100: # Broadly matching ISBN/Title usually shouldn't be 188k
            docs = data.get("response", {}).get("docs", [])
            for i, d in enumerate(docs):
                doc = d.get("doc", {})
                print(f"  [{i+1}] {doc.get('bookname')} | {doc.get('authors')}")
        elif num_found >= 180000:
            print("!! Still filtered out to the whole catalog !!")
        else:
            print("No results found.")
            err = data.get("response", {}).get("error")
            if err: print(f"API Error: {err}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 세계 도시 여행 - 9791190136952
    test_itemsrch_with_dates("9791190136952", "세계 도시 여행")
    # 검은 새 - 9788955827057
    test_itemsrch_with_dates("9788955827057", "검은 새")
