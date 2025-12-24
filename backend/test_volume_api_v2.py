"""권차 API 테스트 (날짜 파라미터 추가)"""
import requests
from datetime import datetime, timedelta
from core.config import DATA4LIBRARY_KEY
from core.database import supabase

PANGYO_LIB_CODE = "141231"

# 날짜 설정 (최근 5년)
end_date = datetime.now()
start_date = end_date - timedelta(days=365*5)

# 테스트할 책 가져오기
response = supabase.table("childbook_items")\
    .select("isbn, title, pangyo_callno")\
    .not_.is_("pangyo_callno", "null")\
    .not_.is_("isbn", "null")\
    .limit(3)\
    .execute()

books = response.data

print(f"Testing {len(books)} books:\n")
print(f"Date range: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}\n")

for book in books:
    isbn = book['isbn']
    title = book['title']
    callno = book['pangyo_callno']
    
    print(f"Book: {title}")
    print(f"ISBN: {isbn}")
    print(f"Call No: {callno}")
    
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "isbn13": isbn,
        "startDt": start_date.strftime("%Y-%m-%d"),
        "endDt": end_date.strftime("%Y-%m-%d"),
        "format": "json",
        "pageSize": 100
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        print(f"API Response:")
        print(f"  Status: {resp.status_code}")
        
        result = data.get("response", {}).get("result", [])
        print(f"  Result count: {len(result)}")
        
        if result:
            for i, item in enumerate(result, 1):
                vol = item.get("vol", "")
                bookname = item.get("bookname", "")
                print(f"  Item {i}:")
                print(f"    - bookname: {bookname}")
                print(f"    - vol: '{vol}'")
        else:
            error_msg = data.get("response", {}).get("error", {}).get("message", "")
            if error_msg:
                print(f"  Error: {error_msg}")
            else:
                print(f"  No results found")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    print("-" * 80)
    print()
