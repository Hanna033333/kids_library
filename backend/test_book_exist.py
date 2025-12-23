import requests
from core.config import DATA4LIBRARY_KEY

def test_book_exist(isbn, title):
    url = "http://data4library.kr/api/bookExist"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "isbn13": isbn,
        "format": "json"
    }
    
    print(f"\n--- Testing bookExist: {title} ({isbn}) ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        result = data.get("response", {}).get("result", {})
        has_book = result.get("hasBook")
        loan_avai = result.get("loanAvailable")
        
        print(f"Has Book: {has_book}")
        print(f"Loan Available: {loan_avai}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    samples = [
        ("9788955827057", "검은 새"),
        ("9791160406238", "금방울전"),
        ("9791175240421", "오즈의 마법사")
    ]
    
    for isbn, title in samples:
        test_book_exist(isbn, title)
