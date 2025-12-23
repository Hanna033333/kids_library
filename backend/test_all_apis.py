import requests
import json
from core.config import DATA4LIBRARY_KEY

def test_api(api_name, params):
    url = f"http://data4library.kr/api/{api_name}"
    params["authKey"] = DATA4LIBRARY_KEY
    params["format"] = "json"
    
    print(f"\n--- Testing API: {api_name} | Params: {list(params.keys())} ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        # print("Raw Text:", response.text[:200])
        data = response.json()
        
        resp = data.get("response", {})
        if "error" in resp:
            print(f"API Error: {resp['error']}")
        
        num_found = resp.get("numFound", 0)
        print(f"NumFound: {num_found}")
        
        if num_found > 0:
            docs = resp.get("docs", [])
            if docs:
                doc = docs[0].get("doc", {})
                print(f"Match: {doc.get('bookname')} | {doc.get('authors')}")
                if "callNumbers" in doc:
                    print(f"CallNumbers exist!")
                elif "call_no" in doc:
                    print(f"CallNo: {doc.get('call_no')}")
        
        # Check result (for some APIs it's in result)
        if "result" in resp:
            print(f"Result: {resp['result']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_isbn = "9788955827057" # 검은 새
    
    # Test srchLibLendingBook
    test_api("srchLibLendingBook", {"libCode": "141231", "isbn13": test_isbn})
    
    # Test srchBooks
    test_api("srchBooks", {"libCode": "141231", "isbn13": test_isbn})
    
    # Test srchBooks with keyword
    test_api("srchBooks", {"libCode": "141231", "keyword": "검은 새"})
    
    # Test itemSrch again with DIFFERENT params
    # maybe it's ISBN13 (caps) or isbn (short)
    test_api("itemSrch", {"libCode": "141231", "isbn13": test_isbn})
    test_api("itemSrch", {"libCode": "141231", "type": "ISBN", "isbn13": test_isbn})
