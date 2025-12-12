"""
data4library API에서 전체 청구기호 문자열 필드 확인
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

print("=" * 60)
print("1. itemSrch API에서 전체 청구기호 문자열 필드 확인")
print("=" * 60)
print()

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

try:
    res = requests.get(url, params=params, timeout=30)
    data = res.json()
    docs = data.get("response", {}).get("docs", [])
    
    # '밤마다 환상축제' 찾기
    target_book = None
    for doc in docs:
        item = doc.get("doc", {})
        if "밤마다 환상축제" in item.get("bookname", ""):
            target_book = item
            break
    
    if target_book:
        print(f"✅ 책 찾음: {target_book.get('bookname', '')}")
        print()
        print("전체 필드에서 'callNumber' 문자열 필드 찾기:")
        print("-" * 60)
        
        # callNumber가 문자열로 있는지 확인
        if "callNumber" in target_book:
            print(f"✅ callNumber (문자열): {target_book['callNumber']}")
        else:
            print("❌ callNumber 필드 없음")
        
        # 다른 가능한 필드명들 확인
        possible_fields = ['callno', 'call_no', 'callNumber', 'fullCallNumber', 'call_number', 'full_callno']
        found_fields = []
        for field in possible_fields:
            if field in target_book:
                found_fields.append((field, target_book[field]))
                print(f"✅ {field}: {target_book[field]}")
        
        if not found_fields:
            print("❌ 전체 청구기호 문자열 필드를 찾을 수 없습니다.")
        
        print()
        print("doc 객체의 모든 키:")
        for key in sorted(target_book.keys()):
            print(f"  - {key}")
    
    print()
    print("=" * 60)
    print("2. bookExist API 응답 구조 확인")
    print("=" * 60)
    print()
    
    # bookExist API 테스트
    book_exist_url = "http://data4library.kr/api/bookExist"
    book_exist_params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "isbn13": "9788901238678",  # 밤마다 환상축제
        "format": "json"
    }
    
    res2 = requests.get(book_exist_url, params=book_exist_params, timeout=10)
    book_exist_data = res2.json()
    
    print("bookExist API 응답:")
    print(json.dumps(book_exist_data, ensure_ascii=False, indent=2))
    
    # callNumber 필드 확인
    response = book_exist_data.get("response", {})
    if "callNumber" in response:
        print(f"\n✅ callNumber 필드 발견: {response['callNumber']}")
    else:
        print("\n❌ callNumber 필드 없음")
        print("응답의 모든 키:")
        for key in sorted(response.keys()):
            print(f"  - {key}: {response[key]}")

except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc()






