import requests
import json
from core.config import DATA4LIBRARY_KEY

def test_api_sample(isbn, title):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "type": "ISBN",
        "keyword": isbn,
        "format": "json"
    }
    
    print(f"\n--- Testing ISBN Search: {title} ({isbn}) ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        if docs:
            doc = docs[0].get("doc", {})
            print(f"Result Title: {doc.get('bookname')}")
            if doc.get('bookname') == "대항해시대의 동남아시아":
                print("!! Still getting the default/first book (IP issue likely persists) !!")
            else:
                print("SUCCESS: Got a different book!")
        else:
            print("No results found.")
            err = data.get("response", {}).get("error")
            if err: print(f"API Error: {err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Sample from database
    samples = [
        ("9788955827057", "검은 새"),
        ("9791160406238", "금방울전"),
        ("9791175240421", "오즈의 마법사")
    ]
    
    for isbn, title in samples:
        test_api_sample(isbn, title)
