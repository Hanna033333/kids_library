import requests
from core.config import DATA4LIBRARY_KEY

def test_known_book(isbn, title):
    url = "http://data4library.kr/api/bookExist"
    lib_codes = ["141231", "14123"]
    
    print(f"\n--- Testing Known Book: {title} ({isbn}) ---")
    for code in lib_codes:
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": code,
            "isbn13": isbn,
            "format": "json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            # print(json.dumps(data, indent=2, ensure_ascii=False)) # too much
            
            result = data.get("response", {}).get("result", {})
            has_book = result.get("hasBook")
            
            if has_book == "Y":
                print(f"SUCCESS: LibCode {code} has the book!")
            else:
                error = data.get("response", {}).get("error")
                if error:
                    print(f"LibCode {code} Error: {error}")
                else:
                    print(f"LibCode {code}: Has Book: {has_book}")
                
        except Exception as e:
            print(f"Error for {code}: {e}")

if __name__ == "__main__":
    # "세계 도시 여행" - 9791190136952 (Definitly in Pangyo according to childbook_items)
    test_known_book("9791190136952", "세계 도시 여행")
