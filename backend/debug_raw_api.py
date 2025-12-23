import requests
import json
from core.config import DATA4LIBRARY_KEY

def check_one_book(isbn):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "type": "ISBN",
        "keyword": isbn,
        "format": "json"
    }
    
    response = requests.get(url, params=params)
    print(f"Status: {response.status_code}")
    print("Response JSON:")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text[:500])

if __name__ == "__main__":
    # 검은 새: 9788955827057
    check_one_book("9788955827057")
