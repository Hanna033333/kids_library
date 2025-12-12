"""
전체 청구기호 구조 확인 - '밤마다 환상축제' 책 찾기
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

# '밤마다 환상축제' 책 찾기 (더 짧은 기간으로 시도)
params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": "2024-01-01",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 500,
    "format": "json"
}

print("=" * 60)
print("'밤마다 환상축제' 책의 전체 청구기호 구조 확인")
print("=" * 60)
print()

try:
    res = requests.get(url, params=params, timeout=120)
    res.raise_for_status()
    
    if not res.text:
        print("❌ 빈 응답")
        exit(1)
    
    try:
        data = res.json()
    except ValueError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        print(f"응답 내용 (처음 500자): {res.text[:500]}")
        exit(1)
    
    docs = data.get("response", {}).get("docs", [])
except requests.exceptions.RequestException as e:
    print(f"❌ 요청 오류: {e}")
    exit(1)

# '밤마다 환상축제' 찾기
target_book = None
for doc in docs:
    item = doc.get("doc", {})
    title = item.get("bookname", "")
    if "밤마다 환상축제" in title or "환상축제" in title:
        target_book = item
        break

if target_book:
    print(f"✅ 책 찾음: {target_book.get('bookname', '')}")
    print()
    print("전체 doc 구조:")
    print("-" * 60)
    for key, value in target_book.items():
        if key == "callNumbers":
            print(f"{key}:")
            print(json.dumps(value, ensure_ascii=False, indent=2))
        else:
            print(f"{key}: {value}")
    print("-" * 60)
    print()
    
    # callNumbers 상세 분석
    call_numbers = target_book.get("callNumbers", [])
    print(f"callNumbers 배열 개수: {len(call_numbers)}")
    print()
    
    for i, call_info in enumerate(call_numbers, 1):
        print(f"callNumbers[{i-1}]:")
        call_number = call_info.get("callNumber", {})
        print(json.dumps(call_number, ensure_ascii=False, indent=4))
        print()
        
        # 각 필드 확인
        print("  주요 필드:")
        for key, value in call_number.items():
            print(f"    {key}: {value}")
        print()
else:
    print("❌ '밤마다 환상축제' 책을 찾을 수 없습니다.")
    print()
    print("대신 아동 도서 샘플 확인:")
    print("-" * 60)
    
    # 아동 도서 샘플 찾기
    found_sample = False
    for doc in docs:
        item = doc.get("doc", {})
        call_numbers = item.get("callNumbers", [])
        
        for call_info in call_numbers:
            call_number = call_info.get("callNumber", {})
            separate_shelf_name = call_number.get("separate_shelf_name", "")
            
            if separate_shelf_name and (separate_shelf_name.startswith('아') or separate_shelf_name.startswith('유')):
                print(f"\n책: {item.get('bookname', '')[:50]}")
                print("callNumber 전체 구조:")
                print(json.dumps(call_number, ensure_ascii=False, indent=2))
                found_sample = True
                break
        
        if found_sample:
            break

