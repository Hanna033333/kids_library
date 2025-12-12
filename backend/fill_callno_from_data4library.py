"""
childbook_items에서 pangyo_callno가 없는 책들을 ISBN으로 data4library API에서 검색하여 채우기
"""
from supabase_client import supabase
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

def check_book_exists(isbn: str) -> bool:
    """
    data4library API에서 ISBN으로 판교도서관 소장 여부 확인
    
    Returns:
        소장 여부 (True/False)
    """
    if not isbn or not DATA4LIBRARY_KEY:
        return False
    
    try:
        url = "http://data4library.kr/api/bookExist"
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "isbn13": isbn,
            "libCode": PANGYO_CODE,
            "format": "json"
        }
        
        res = requests.get(url, params=params, timeout=30)
        res.raise_for_status()
        data = res.json()
        
        has_book = data.get("response", {}).get("hasBook", "N") == "Y"
        return has_book
        
    except Exception as e:
        return False

def search_callno_by_isbn(isbn: str) -> str:
    """
    data4library API에서 ISBN으로 판교도서관 청구기호 검색
    
    Returns:
        청구기호 문자열 (예: '유 808.9-ㅇ175ㅇ-204'), 없으면 빈 문자열
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
        for doc_item in docs:
            doc = doc_item.get("doc", {})
            call_numbers = doc.get("callNumbers", [])
            
            if call_numbers:
                for call_info in call_numbers:
                    # 판교도서관 확인
                    lib_name = call_info.get("libName", "")
                    lib_code = str(call_info.get("libCode", ""))
                    
                    if "판교" in lib_name or PANGYO_CODE in lib_code:
                        call_number = call_info.get("callNumber", {})
                        
                        # 청구기호 구성
                        parts = []
                        
                        # 1. separate_shelf_name (유/아)
                        separate_shelf_name = call_number.get("separate_shelf_name", "")
                        if separate_shelf_name:
                            parts.append(separate_shelf_name)
                        
                        # 2. class_no (KDC 분류번호)
                        class_no = call_number.get("class_no", "")
                        if class_no:
                            parts.append(class_no)
                        
                        # 3. book_code
                        book_code = call_number.get("book_code", "")
                        if book_code:
                            parts.append(book_code)
                        
                        # 4. copy_code (총서 번호)
                        copy_code = call_number.get("copy_code", "")
                        if copy_code:
                            parts.append(copy_code)
                        
                        # 청구기호 조합: '유 808.9-ㅇ175ㅇ-204' 형식
                        if len(parts) >= 3:
                            # 첫 번째는 공백, 나머지는 하이픈으로 연결
                            callno = parts[0]
                            if len(parts) > 1:
                                callno += " " + "-".join(parts[1:])
                            return callno
                        elif len(parts) == 2:
                            return " ".join(parts)
                        elif len(parts) == 1:
                            return parts[0]
            
            # callNumbers가 없으면 다른 필드 확인
            callno = doc.get("callno", "")
            if callno:
                return callno
        
        return ""
        
    except Exception as e:
        return ""

print("=" * 60)
print("ISBN 기준 data4library API 청구기호 검색 및 채우기")
print("=" * 60)
print()

# childbook_items에서 pangyo_callno가 없는 항목 조회
print("1. childbook_items에서 pangyo_callno가 없는 항목 조회 중...")

items_to_search = []
page = 0
page_size = 1000

while True:
    res = supabase.table("childbook_items").select("id,isbn,pangyo_callno").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
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
    
    if len(res.data) < page_size:
        break
    page += 1

print(f"   [OK] {len(items_to_search):,}개 항목 발견")
print()

if len(items_to_search) == 0:
    print("처리할 항목이 없습니다.")
    exit(0)

# data4library API에서 청구기호 검색
print("2. data4library API에서 청구기호 검색 중...")
print("   ⚠️  API 호출이므로 시간이 걸릴 수 있습니다.")
print()

success_count = 0
not_found_count = 0
fail_count = 0

for idx, item in enumerate(items_to_search):
    child_id = item['child_id']
    isbn = item['isbn']
    
    # 1단계: 소장 여부 확인
    exists = check_book_exists(isbn)
    
    if not exists:
        # 소장되지 않음 -> '없음'으로 설정
        try:
            supabase.table("childbook_items").update({
                "pangyo_callno": "없음"
            }).eq("id", child_id).execute()
            not_found_count += 1
        except Exception as e:
            fail_count += 1
            if fail_count <= 5:
                print(f"   [ERROR] ID {child_id} 업데이트 실패: {e}")
    else:
        # 2단계: 소장되어 있으면 청구기호 가져오기
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
            # 소장은 되는데 청구기호를 못 찾은 경우
            not_found_count += 1
    
    # 진행 상황 출력 (50개마다)
    if (idx + 1) % 50 == 0:
        progress_pct = (idx + 1) / len(items_to_search) * 100
        print(f"   진행 중: {idx + 1}/{len(items_to_search)} ({progress_pct:.1f}%) | 성공: {success_count}, 찾지못함: {not_found_count}, 실패: {fail_count}")
        sys.stdout.flush()
    
    # 첫 번째 항목과 마지막 항목도 출력
    if idx == 0:
        print(f"   시작: ID {child_id}, ISBN {isbn}")
        sys.stdout.flush()
    
    # API 호출 제한 고려 (초당 1회 정도)
    time.sleep(0.1)

print()
print("=" * 60)
print("[OK] 완료!")
print("-" * 60)
print(f"총 처리: {len(items_to_search):,}개")
print(f"성공 (청구기호 찾음): {success_count:,}개")
print(f"소장 안됨/찾지 못함: {not_found_count:,}개")
print(f"실패: {fail_count:,}개")
print("=" * 60)

