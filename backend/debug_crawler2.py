import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from crawler import is_child_book, PANGYO_CODE, DATA4LIBRARY_KEY

env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

url = "http://data4library.kr/api/itemSrch"
page = 1
page_size = 100
start_dt = "2024-01-01"
end_dt = "2024-12-31"

params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": start_dt,
    "endDt": end_dt,
    "pageNo": page,
    "pageSize": page_size,
    "format": "json"
}

print(f"API 호출 시작...")
print(f"파라미터: {params}")

try:
    res = requests.get(url, params=params, timeout=60)
    print(f"응답 상태: {res.status_code}")
    
    if res.status_code != 200:
        print(f"API 오류: {res.status_code} - {res.text[:200]}")
    else:
        data = res.json()
        print(f"응답 키: {list(data.keys())}")
        
        if "error" in data.get("response", {}):
            print(f"API 에러: {data['response']['error']}")
        else:
            docs = data.get("response", {}).get("docs", [])
            print(f"docs 개수: {len(docs)}")
            
            if not docs:
                print("데이터 없음!")
            else:
                child_count = 0
                for d in docs:
                    item = d.get("doc", {})
                    class_no = item.get("class_no", "")
                    if is_child_book(class_no):
                        child_count += 1
                        print(f"아동 도서 발견: {item.get('bookname', '')} (KDC: {class_no})")
                
                print(f"\n총 아동 도서: {child_count}권")
                
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()










