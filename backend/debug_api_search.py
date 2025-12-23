import requests
from core.config import DATA4LIBRARY_KEY

def test_api(keyword, lib_code):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": lib_code,
        "type": "ALL",
        "keyword": keyword,
        "format": "json",
        "pageNo": 1,
        "pageSize": 5
    }
    
    print(f"\n--- Testing Keyword: '{keyword}' | LibCode: {lib_code} ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            num_found = data.get("response", {}).get("numFound", 0)
            print(f"NumFound: {num_found}")
            if num_found > 0:
                docs = data.get("response", {}).get("docs", [])
                for i, d in enumerate(docs[:3]):
                    doc = d.get("doc", {})
                    print(f"Result {i+1}: {doc.get('bookname')} | {doc.get('authors')}")
            else:
                print("No results found.")
                # Print error message if any
                err = data.get("response", {}).get("error", "")
                if err: print(f"API Error: {err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test '오즈의 마법사' with both codes
    test_api("오즈의 마법사", "141231") # Pangyo (standard)
    test_api("오즈의 마법사", "14123")  # User mentioned
    
    # Test a book the user likely knows is there
    test_api("어린이 민담집", "141231")
