import requests
import json
import time

TTBKEY = "ttbrkdgkssk011716001"
TEST_ISBN = "9788936446819" 

def test_api():
    url = "https://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        "ttbkey": TTBKEY,
        "itemIdType": "ISBN13",
        "ItemId": TEST_ISBN,
        "output": "js",
        "Version": "20131101",
        "Cover": "Big"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Requesting to {url} with headers...")
    try:
        start = time.time()
        # Timeout 5 seconds
        response = requests.get(url, params=params, headers=headers, timeout=5)
        duration = time.time() - start
        
        print(f"Response received in {duration:.2f}s")
        print(f"Status Code: {response.status_code}")
        print("Raw Response prefix:")
        print(response.text[:200])
        
        data = response.json()
        print("\nParsed JSON:")
        # print(json.dumps(data, indent=2, ensure_ascii=False)) # too long
        if "errorMessage" in data:
             print(f"API Error: {data['errorMessage']}")
        elif "item" in data:
             print(f"Success! Item Count: {len(data['item'])}")
             if len(data['item']) > 0:
                 print(f"Cover URL: {data['item'][0].get('cover')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
