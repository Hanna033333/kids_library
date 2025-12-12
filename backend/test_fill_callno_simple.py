"""간단한 테스트 - 몇 개만 처리"""
from supabase_client import supabase
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
print("간단한 테스트 (5개만)")
print("=" * 60)
print()

# childbook_items에서 pangyo_callno가 없는 항목 5개만 조회
print("1. 데이터 조회 중...")
res = supabase.table("childbook_items").select("id,isbn,pangyo_callno").limit(100).execute()

items_to_search = []
for item in res.data:
    pangyo_callno = item.get("pangyo_callno")
    has_pangyo_callno = pangyo_callno and len(str(pangyo_callno).strip()) > 0 and str(pangyo_callno).strip() != "없음"
    
    if not has_pangyo_callno:
        isbn = item.get("isbn")
        if isbn and len(str(isbn).strip()) > 0:
            items_to_search.append({
                'child_id': item.get('id'),
                'isbn': str(isbn).strip()
            })
            if len(items_to_search) >= 5:
                break

print(f"   테스트 항목: {len(items_to_search)}개")
print()

# 각 항목 테스트
for idx, item in enumerate(items_to_search):
    child_id = item['child_id']
    isbn = item['isbn']
    
    print(f"[{idx + 1}/{len(items_to_search)}] ID: {child_id}, ISBN: {isbn}")
    
    # API 호출
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "isbn": isbn,
        "pageNo": 1,
        "pageSize": 10,
        "format": "json"
    }
    
    try:
        res = requests.get(url, params=params, timeout=30)
        data = res.json()
        docs = data.get("response", {}).get("docs", [])
        
        if docs:
            doc = docs[0].get("doc", {})
            call_numbers = doc.get("callNumbers", [])
            
            found_callno = None
            for call_info in call_numbers:
                lib_name = call_info.get("libName", "")
                if "판교" in lib_name:
                    call_number = call_info.get("callNumber", {})
                    parts = []
                    if call_number.get("separate_shelf_name"):
                        parts.append(call_number.get("separate_shelf_name"))
                    if call_number.get("class_no"):
                        parts.append(call_number.get("class_no"))
                    if call_number.get("book_code"):
                        parts.append(call_number.get("book_code"))
                    if call_number.get("copy_code"):
                        parts.append(call_number.get("copy_code"))
                    
                    if len(parts) >= 3:
                        found_callno = parts[0] + " " + "-".join(parts[1:])
                    elif len(parts) > 0:
                        found_callno = " ".join(parts)
                    break
            
            if found_callno:
                print(f"  ✅ 청구기호 찾음: {found_callno}")
            else:
                print(f"  ❌ 청구기호 찾지 못함")
        else:
            print(f"  ❌ 검색 결과 없음")
            
    except Exception as e:
        print(f"  ❌ 오류: {e}")
    
    print()

print("=" * 60)

