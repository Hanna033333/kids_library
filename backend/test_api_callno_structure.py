"""
API 응답에서 실제 청구기호 구조 확인
"""
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
import json

env_path = Path(__file__).parent / ".env"
try:
    load_dotenv(dotenv_path=env_path)
except Exception:
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    try:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
                    except:
                        pass

DATA4LIBRARY_KEY = os.getenv("DATA4LIBRARY_KEY")
PANGYO_CODE = "141231"

url = "http://data4library.kr/api/itemSrch"

params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": "2024-12-01",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 50,
    "format": "json"
}

print("=" * 60)
print("API 응답에서 아동 도서의 청구기호 구조 확인")
print("=" * 60)
print()

res = requests.get(url, params=params, timeout=30)
data = res.json()
docs = data.get("response", {}).get("docs", [])

print(f"총 {len(docs)}건 확인")
print()

child_books = []
for doc in docs:
    item = doc.get("doc", {})
    call_numbers = item.get("callNumbers", [])
    
    # 아동 도서 확인
    is_child = False
    actual_callno = None
    
    for call_info in call_numbers:
        call_number = call_info.get("callNumber", {})
        separate_shelf_name = call_number.get("separate_shelf_name", "")
        shelf_loc_name = call_number.get("shelf_loc_name", "")
        book_code = call_number.get("book_code", "")
        
        if (separate_shelf_name and (separate_shelf_name.startswith('아') or separate_shelf_name.startswith('유'))) or \
           ('어린이' in shelf_loc_name):
            is_child = True
            # 실제 청구기호 찾기
            if book_code:
                actual_callno = book_code
            elif separate_shelf_name:
                actual_callno = separate_shelf_name
            break
    
    if is_child:
        child_books.append({
            "title": item.get("bookname", ""),
            "class_no": item.get("class_no", ""),
            "actual_callno": actual_callno,
            "callNumbers": call_numbers
        })

print(f"아동 도서 발견: {len(child_books)}건")
print()

# 처음 5개 상세 출력
for i, book in enumerate(child_books[:5], 1):
    print(f"{i}. {book['title'][:50]}")
    print(f"   class_no: {book['class_no']}")
    print(f"   actual_callno: {book['actual_callno']}")
    print(f"   callNumbers 구조:")
    for cn in book['callNumbers']:
        cn_detail = cn.get('callNumber', {})
        print(f"     - separate_shelf_name: {cn_detail.get('separate_shelf_name', '')}")
        print(f"     - book_code: {cn_detail.get('book_code', '')}")
        print(f"     - shelf_loc_name: {cn_detail.get('shelf_loc_name', '')}")
    print()






