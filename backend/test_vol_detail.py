import requests
from core.config import DATA4LIBRARY_KEY
from datetime import datetime
import json

PANGYO_LIB_CODE = "141231"

def call_api(endpoint, params):
    url = f"http://data4library.kr/api/{endpoint}"
    params["authKey"] = DATA4LIBRARY_KEY
    params["format"] = "json"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def test_book(isbn, title):
    print(f"\n🔍 Testing: {title} ({isbn})")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. itemSrch (도서관별 장서 조회)
    res_itemsrch = call_api("itemSrch", {
        "libCode": PANGYO_LIB_CODE,
        "type": "isbn",
        "keyword": isbn,
        "startDt": "2000-01-01",
        "endDt": today
    })
    
    # 2. libSrchByBook (도서관별 소장권수 및 대출가능권수 조회)
    res_libbook = call_api("libSrchByBook", {
        "isbn": isbn,
        "libCode": PANGYO_LIB_CODE
    })
    
    print("--- itemSrch Results ---")
    docs = res_itemsrch.get("response", {}).get("docs", [])
    if docs:
        for i, d in enumerate(docs[:2]):
            doc = d.get("doc", {})
            print(f"  [{i+1}] vol: '{doc.get('vol')}', call_no: '{doc.get('call_no')}', shelf_loc: '{doc.get('shelf_loc')}'")
            if i == 0:
                # Use json.dumps instead of direct f-string dict
                clean_doc = {k: v for k, v in doc.items() if v}
                print(f"      Full doc snippet: {json.dumps(clean_doc, ensure_ascii=False)}")
    else:
        err = res_itemsrch.get("response", {}).get("error")
        print(f"  No docs found. API Error: {err}" if err else "  No docs found.")

    print("--- libSrchByBook Results ---")
    # libSrchByBook returns list of libraries
    libs = res_libbook.get("response", {}).get("libs", [])
    if libs:
        for i, l in enumerate(libs):
            lib = l.get("lib", {})
            print(f"  Lib: {lib.get('libName')}, Code: {lib.get('libCode')}")
    else:
        err = res_libbook.get("response", {}).get("error")
        print(f"  No lib info found. API Error: {err}" if err else "  No lib info found.")

def main():
    # 10개 테스트 데이터
    test_data = [
        ('9788949113760', '안녕, 나의 등대'),
        ('9788931454109', '마인크래프트'),
        ('9788936441753', '문제아'),
        # 만화/시리즈로 추정되는 것들 추가 가능
    ]
    
    for isbn, title in test_data:
        test_book(isbn, title)

if __name__ == "__main__":
    main()
