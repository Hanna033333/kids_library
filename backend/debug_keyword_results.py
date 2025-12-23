import requests
import json
from core.config import DATA4LIBRARY_KEY

def test_keyword(keyword):
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": "141231",
        "type": "ALL",
        "keyword": keyword,
        "format": "json"
    }
    
    response = requests.get(url, params=params)
    print(f"Keyword: {keyword}")
    try:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        if docs:
            doc = docs[0].get("doc", {})
            print(f"  First Doc: {doc.get('bookname')} | {doc.get('authors')}")
            print(f"  Class No: {doc.get('class_no')}")
            call_nums = doc.get("callNumbers", [])
            if call_nums:
                cn = call_nums[0].get("callNumber", {})
                print(f"  Call Num Parts: {cn.get('separate_shelf_code')}, {doc.get('class_no')}, {cn.get('book_code')}")
        else:
            print("  No docs found.")
            print(f"  Error: {data.get('response', {}).get('error')}")
    except:
        print("  Failed to parse JSON.")

if __name__ == "__main__":
    test_keyword("검은 새 길벗어린이 이수지")
    test_keyword("금방울전 한겨레아이들 임정자")
    test_keyword("오즈의 마법사 시공주니어 라이먼 프랭크 바움")
