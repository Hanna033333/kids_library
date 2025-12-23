import requests
from core.config import DATA4LIBRARY_KEY

def test_param_names(val):
    url = "http://data4library.kr/api/itemSrch"
    param_names = ["keyword", "query", "q", "isbn"]
    
    for name in param_names:
        print(f"\n--- Testing Param Name: {name}='{val}' ---")
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": "141231",
            "type": "ALL",
            name: val,
            "format": "json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            num_found = data.get("response", {}).get("numFound", 0)
            print(f"NumFound: {num_found}")
            if 0 < num_found < 1000:
                print(f"SUCCESS! {name} works.")
                doc = data["response"]["docs"][0]["doc"]
                print(f"Match: {doc['bookname']}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_param_names("9791190136952")
