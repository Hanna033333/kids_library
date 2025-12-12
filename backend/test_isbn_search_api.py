"""data4library API ISBN 검색 테스트"""
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
env_path = Path(__file__).parent / ".env"
try:
    load_dotenv(dotenv_path=env_path)
except Exception:
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if key and value:
                                os.environ[key] = value
                        except Exception:
                            continue
        except Exception:
            pass

DATA4LIBRARY_KEY = os.getenv("DATA4LIBRARY_KEY")
PANGYO_CODE = "141231"

print("=" * 60)
print("data4library API ISBN 검색 테스트")
print("=" * 60)
print()

# 테스트 ISBN
test_isbn = "9788936442484"  # 거짓말이 가득

print(f"테스트 ISBN: {test_isbn}")
print()

url = "http://data4library.kr/api/itemSrch"
params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "isbn": test_isbn,
    "pageNo": 1,
    "pageSize": 10,
    "format": "json"
}

print(f"API URL: {url}")
print(f"파라미터: {params}")
print()

try:
    res = requests.get(url, params=params, timeout=30)
    print(f"상태 코드: {res.status_code}")
    print()
    
    if res.status_code == 200:
        data = res.json()
        print("응답 구조:")
        print(f"  response: {list(data.get('response', {}).keys())}")
        print()
        
        docs = data.get("response", {}).get("docs", [])
        print(f"검색 결과: {len(docs)}개")
        print()
        
        if docs:
            doc = docs[0].get("doc", {})
            print("첫 번째 결과:")
            print(f"  제목: {doc.get('bookname', '')}")
            print(f"  ISBN13: {doc.get('isbn13', '')}")
            print(f"  ISBN: {doc.get('isbn', '')}")
            print()
            
            call_numbers = doc.get("callNumbers", [])
            print(f"청구기호 정보: {len(call_numbers)}개")
            
            for idx, call_info in enumerate(call_numbers):
                call_number = call_info.get("callNumber", {})
                print(f"\n  [{idx+1}] 청구기호:")
                print(f"    separate_shelf_name: {call_number.get('separate_shelf_name', '')}")
                print(f"    class_no: {call_number.get('class_no', '')}")
                print(f"    book_code: {call_number.get('book_code', '')}")
                print(f"    copy_code: {call_number.get('copy_code', '')}")
                print(f"    shelf_loc_name: {call_number.get('shelf_loc_name', '')}")
                print(f"    libName: {call_info.get('libName', '')}")
                
                # 전체 청구기호 구성
                parts = []
                if call_number.get('separate_shelf_name'):
                    parts.append(call_number.get('separate_shelf_name'))
                if call_number.get('class_no'):
                    parts.append(call_number.get('class_no'))
                if call_number.get('book_code'):
                    parts.append(call_number.get('book_code'))
                if call_number.get('copy_code'):
                    parts.append(call_number.get('copy_code'))
                
                full_callno = ' '.join(parts) if parts else '없음'
                print(f"    전체 청구기호: {full_callno}")
        else:
            print("검색 결과가 없습니다.")
    else:
        print(f"오류: {res.text[:500]}")
        
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)

