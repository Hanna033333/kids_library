import requests
from core.config import DATA4LIBRARY_KEY

def test_itemsrch_known(isbn, title):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "type": "ISBN",
        "keyword": isbn,
        "format": "json"
    }
    
    print(f"\n--- Testing itemSrch for Known Book: {title} ({isbn}) ---")
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        docs = data.get("response", {}).get("docs", [])
        if docs:
            doc = docs[0].get("doc", {})
            print(f"Match Found: {doc.get('bookname')}")
            print(f"Class No: {doc.get('class_no')}")
            cn_list = doc.get("callNumbers", [])
            if cn_list:
                cn = cn_list[0].get("callNumber", {})
                print(f"Call Number: {cn.get('separate_shelf_code')} {doc.get('class_no')}-{cn.get('book_code')}")
            else:
                print("No call number information in response.")
        else:
            print("No results found in itemSrch.")
            err = data.get("response", {}).get("error")
            if err: print(f"API Error: {err}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 세계 도시 여행 - 9791190136952
    test_itemsrch_known("9791190136952", "세계 도시 여행")
