import requests
from core.config import DATA4LIBRARY_KEY
import json

def test_minimal():
    isbn = "9791190136952" # 세계 도시 여행
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "type": "isbn",
        "keyword": isbn,
        "format": "json",
        "startDt": "2000-01-01",
        "endDt": "2025-12-22"
    }
    
    print(f"Testing ISBN: {isbn}")
    response = requests.get(url, params=params)
    print(f"Status: {response.status_code}")
    print("Response:")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)

if __name__ == "__main__":
    test_minimal()
