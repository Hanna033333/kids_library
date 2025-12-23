import requests
from core.config import DATA4LIBRARY_KEY

def test_exhaustive_params(val):
    url = "http://data4library.kr/api/itemSrch"
    lib_code = "141231"
    
    params_to_test = [
        {"type": "ISBN", "keyword": val},
        {"type": "isbn", "keyword": val},
        {"type": "ISBN", "isbn13": val},
        {"type": "ISBN", "isbn": val},
        {"isbn13": val},
        {"isbn": val},
        {"keyword": val},
        {"type": "all", "keyword": val},
        {"type": "TITLE", "keyword": "검은 새"}
    ]
    
    for p in params_to_test:
        p["authKey"] = DATA4LIBRARY_KEY
        p["libCode"] = lib_code
        p["format"] = "json"
        
        print(f"\n--- Testing: {p} ---")
        try:
            response = requests.get(url, params=p, timeout=10)
            data = response.json()
            num = data.get("response", {}).get("numFound", 0)
            print(f"NumFound: {num}")
            if 0 < num < 1000:
                print("!!! SUCCESS !!!")
                docs = data["response"].get("docs", [])
                if docs:
                    print(f"Match: {docs[0].get('doc', {}).get('bookname')}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_isbn = "9788955827057" # 검은 새
    test_exhaustive_params(test_isbn)
