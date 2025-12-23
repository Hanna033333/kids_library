import requests
import json
from core.config import DATA4LIBRARY_KEY

def test_srch_dtl():
    url = "http://data4library.kr/api/srchDtlList"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "isbn13": "9788955827057",
        "libCode": "141231",
        "format": "json"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    print("Full Response Keys:", data.keys())
    if "response" in data:
        resp = data["response"]
        print("Response Keys:", resp.keys())
        if "detail" in resp:
            print("Detail exists!")
            detail = resp["detail"]
            if detail:
                book = detail[0].get("book", {})
                print("Book Keys:", book.keys())
                print("Call Numbers:", book.get("callNumbers"))
                print("Class No:", book.get("class_no"))

if __name__ == "__main__":
    test_srch_dtl()
