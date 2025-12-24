"""실제 DB ISBN으로 권차 테스트"""
import requests
import json
from datetime import datetime, timedelta
from core.config import DATA4LIBRARY_KEY
from core.database import supabase

PANGYO_LIB_CODE = "141231"
end_date = datetime.now()
start_date = end_date - timedelta(days=365*10)  # 10년으로 확장

# 실제 DB에서 ISBN 가져오기
response = supabase.table("childbook_items")\
    .select("isbn, title, pangyo_callno")\
    .not_.is_("isbn", "null")\
    .not_.is_("pangyo_callno", "null")\
    .limit(1)\
    .execute()

if not response.data:
    print("No books found")
    exit()

book = response.data[0]
test_isbn = book['isbn']
title = book['title']
callno = book['pangyo_callno']

print(f"Testing with actual DB book:")
print(f"Title: {title}")
print(f"ISBN: {test_isbn}")
print(f"Call No: {callno}\n")

url = "http://data4library.kr/api/itemSrch"
params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_LIB_CODE,
    "isbn13": test_isbn,
    "startDt": start_date.strftime("%Y-%m-%d"),
    "endDt": end_date.strftime("%Y-%m-%d"),
    "format": "json",
    "pageSize": 100
}

resp = requests.get(url, params=params, timeout=10)
data = resp.json()

print(f"API Response:")
print(f"Status: {resp.status_code}")
print(f"numFound: {data.get('response', {}).get('numFound', 0)}")
print(f"resultNum: {data.get('response', {}).get('resultNum', 0)}\n")

result = data.get("response", {}).get("result", [])
if result:
    print(f"Found {len(result)} items:")
    for i, item in enumerate(result, 1):
        print(f"\nItem {i}:")
        print(f"  bookname: {item.get('bookname', '')}")
        print(f"  vol: '{item.get('vol', '')}'")
        print(f"  class_no: {item.get('class_no', '')}")
        print(f"  reg_no: {item.get('reg_no', '')}")
else:
    print("No results found")
    print(f"\nFull response:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
