import requests
from core.config import DATA4LIBRARY_KEY

def test_itemsrch_isbn13_param(isbn):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "isbn13": isbn,
        "format": "json"
    }
    
    print(f"--- Testing itemSrch with isbn13 param: {isbn} ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        num_found = data.get("response", {}).get("numFound", 0)
        print(f"NumFound: {num_found}")
        if 0 < num_found < 100:
            print("SUCCESS! isbn13 param works for itemSrch.")
            doc = data["response"]["docs"][0]["doc"]
            print(f"Match: {doc['bookname']}")
            print(f"Has CallNumbers: {'callNumbers' in doc}")
        else:
            print("Failed to filter by isbn13 param.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 세계 도시 여행 - 9791190136952
    test_itemsrch_isbn13_param("9791190136952")
