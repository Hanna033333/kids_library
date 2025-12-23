import requests
from core.config import DATA4LIBRARY_KEY

def test_lib_codes(isbn, title):
    url = "http://data4library.kr/api/bookExist"
    codes = ["141231", "14123"]
    
    print(f"\n--- Testing ISBN: {title} ({isbn}) ---")
    for code in codes:
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": code,
            "isbn13": isbn,
            "format": "json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            result = data.get("response", {}).get("result", {})
            has_book = result.get("hasBook")
            
            print(f"LibCode {code}: Has Book: {has_book}")
            if has_book == "Y":
                print(f"SUCCESS with LibCode {code}!")
            
            error = data.get("response", {}).get("error")
            if error:
                print(f"LibCode {code} Error: {error}")
                
        except Exception as e:
            print(f"Error for LibCode {code}: {e}")

if __name__ == "__main__":
    test_lib_codes("9788955827057", "검은 새")
