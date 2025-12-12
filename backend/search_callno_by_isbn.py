"""
ISBN 기준으로 data4library API에서 청구기호 검색
"""
from supabase_client import supabase
import csv
import requests
import os
from pathlib import Path
from dotenv import load_dotenv
import time
import sys

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
PANGYO_CODE = "141231"  # 판교도서관 코드

def search_callno_by_isbn(isbn: str) -> str:
    """
    data4library API에서 ISBN으로 판교도서관 청구기호 검색
    
    Returns:
        청구기호 문자열, 없으면 빈 문자열
    """
    if not isbn or not DATA4LIBRARY_KEY:
        return ""
    
    try:
        # ISBN으로 검색
        url = "http://data4library.kr/api/itemSrch"
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": PANGYO_CODE,
            "isbn": isbn,
            "pageNo": 1,
            "pageSize": 10,
            "format": "json"
        }
        
        res = requests.get(url, params=params, timeout=30)
        res.raise_for_status()
        data = res.json()
        
        docs = data.get("response", {}).get("docs", [])
        if not docs:
            return ""
        
        # 첫 번째 결과에서 청구기호 찾기
        for doc in docs:
            # callNumbers 필드 확인
            call_numbers = doc.get("callNumbers", [])
            if call_numbers:
                for callno_info in call_numbers:
                    # 판교도서관이고 아동도서인지 확인
                    lib_name = callno_info.get("libName", "")
                    separate_shelf_name = callno_info.get("separateShelfName", "")
                    
                    if "판교" in lib_name or PANGYO_CODE in str(callno_info.get("libCode", "")):
                        callno = callno_info.get("callno", "")
                        if callno:
                            # 아동도서 필터 (선택사항)
                            if separate_shelf_name in ["아", "유"]:
                                return callno
                            # 아동도서가 아니어도 반환
                            return callno
            
            # callNumbers가 없으면 다른 필드 확인
            callno = doc.get("callno", "")
            if callno:
                return callno
        
        return ""
        
    except Exception as e:
        return ""

print("=" * 60)
print("ISBN 기준 data4library API 청구기호 검색")
print("=" * 60)
print()

# CSV 파일 읽기
csv_filename = "no_callno_items.csv"
print(f"1. CSV 파일 읽기: {csv_filename}")

items_to_search = []
try:
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            child_id = row.get('id', '').strip()
            isbn = row.get('isbn', '').strip()
            
            if child_id and isbn:
                items_to_search.append({
                    'child_id': int(child_id),
                    'isbn': isbn
                })
    
    print(f"   [OK] {len(items_to_search):,}개 항목 로드됨")
except Exception as e:
    print(f"   [ERROR] 오류: {e}")
    exit(1)

if len(items_to_search) == 0:
    print("   [WARN] 처리할 항목이 없습니다.")
    exit(0)

print()

# data4library API에서 청구기호 검색
print("2. data4library API에서 청구기호 검색 중...")
print()

success_count = 0
not_found_count = 0
fail_count = 0

for idx, item in enumerate(items_to_search):
    child_id = item['child_id']
    isbn = item['isbn']
    
    callno = search_callno_by_isbn(isbn)
    
    if callno and len(callno.strip()) > 0:
        try:
            supabase.table("childbook_items").update({
                "pangyo_callno": callno.strip()
            }).eq("id", child_id).execute()
            success_count += 1
        except Exception as e:
            fail_count += 1
            if fail_count <= 5:
                print(f"   [ERROR] ID {child_id} 업데이트 실패: {e}")
    else:
        not_found_count += 1
    
    # 진행 상황 출력 (100개마다)
    if (idx + 1) % 100 == 0:
        print(f"   진행 중: {idx + 1}/{len(items_to_search)} (성공: {success_count}, 찾지못함: {not_found_count}, 실패: {fail_count})")
        sys.stdout.flush()
    
    # API 호출 제한 고려
    time.sleep(0.1)

print()
print("=" * 60)
print("[OK] 완료!")
print("-" * 60)
print(f"총 처리: {len(items_to_search):,}개")
print(f"성공 (청구기호 찾음): {success_count:,}개")
print(f"찾지 못함: {not_found_count:,}개")
print(f"실패: {fail_count:,}개")
print("=" * 60)

