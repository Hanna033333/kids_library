"""
callNumbers 필드 상세 분석
"""
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
import json

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DATA4LIBRARY_KEY = os.getenv("DATA4LIBRARY_KEY")
PANGYO_CODE = "141231"

url = "http://data4library.kr/api/itemSrch"

params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": "2024-01-01",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 100,
    "format": "json"
}

print("=" * 60)
print("callNumbers 필드 상세 분석")
print("=" * 60)
print()

res = requests.get(url, params=params, timeout=30)
data = res.json()
docs = data.get("response", {}).get("docs", [])

print(f"총 {len(docs)}건 분석")
print()

# callNumbers 필드 상세 확인
print("callNumbers 필드 상세:")
print("-" * 60)

child_room_keywords = ["어린이", "아동", "유아", "아기"]

for i, doc in enumerate(docs[:20], 1):
    item = doc.get("doc", {})
    title = item.get("bookname", "")
    class_no = item.get("class_no", "")
    call_numbers = item.get("callNumbers", [])
    
    print(f"\n{i}. {title[:40]}")
    print(f"   class_no: {class_no}")
    
    if call_numbers:
        for call_info in call_numbers:
            call_number = call_info.get("callNumber", {})
            shelf_loc_name = call_number.get("shelf_loc_name", "")
            book_code = call_number.get("book_code", "")
            separate_shelf_name = call_number.get("separate_shelf_name", "")
            
            print(f"   shelf_loc_name: {shelf_loc_name}")
            print(f"   book_code: {book_code}")
            print(f"   separate_shelf_name: {separate_shelf_name}")
            
            # 어린이 열람실 관련 키워드 확인
            if any(keyword in shelf_loc_name for keyword in child_room_keywords):
                print(f"   ✅ 어린이 관련 자료실 발견!")
    else:
        print(f"   callNumbers 없음")

print()
print("=" * 60)
print("분석 완료")
print("=" * 60)






