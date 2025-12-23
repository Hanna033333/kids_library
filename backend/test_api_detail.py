import requests
import json
from core.config import DATA4LIBRARY_KEY

def test_api_detail(api_name, params):
    url = f"http://data4library.kr/api/{api_name}"
    params["authKey"] = DATA4LIBRARY_KEY
    params["format"] = "json"
    
    print(f"\n--- Detailed Test: {api_name} ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # Print the first doc in full to see all fields
        docs = data.get("response", {}).get("docs", [])
        if docs:
            print(json.dumps(docs[0].get("doc", {}), indent=2, ensure_ascii=False))
        else:
            print("No docs found.")
            print("Response:", json.dumps(data.get("response", {}), indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_isbn = "9788955827057" # 검은 새
    
    # Test srchBooks with libCode
    test_api_detail("srchBooks", {"libCode": "141231", "isbn13": test_isbn})
    
    # Try srchLibLendingBook with broad date range to avoid period error
    test_api_detail("srchLibLendingBook", {
        "libCode": "141231", 
        "isbn13": test_isbn,
        "startDt": "2000-01-01",
        "endDt": "2025-12-19"
    })
