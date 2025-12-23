import requests
from core.config import DATA4LIBRARY_KEY

def test_itemsrch_variations(isbn, title):
    url = "http://data4library.kr/api/itemSrch"
    
    # Try different combinations
    variations = [
        {"type": "isbn", "keyword": isbn},
        {"type": "title", "keyword": title},
        {"type": "all", "keyword": title}
    ]
    
    for var in variations:
        print(f"\n--- Testing Variation: {var} ---")
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": "141231",
            "type": var["type"],
            "keyword": var["keyword"],
            "format": "json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            num_found = data.get("response", {}).get("numFound", 0)
            print(f"NumFound: {num_found}")
            
            if num_found > 0 and num_found < 180000:
                docs = data.get("response", {}).get("docs", [])
                print(f"Match Found: {docs[0].get('doc', {}).get('bookname')}")
            elif num_found >= 180000:
                print("!! Still getting the whole catalog !!")
            else:
                print("No results found.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # 세계 도시 여행 - 9791190136952
    test_itemsrch_variations("9791190136952", "세계 도시 여행")
