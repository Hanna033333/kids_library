"""
현재 수집이 어느 페이지까지 진행되었는지 확인
"""
from supabase_client import supabase
from crawler import DATA4LIBRARY_KEY, PANGYO_CODE
import requests
from datetime import datetime

print("=" * 60)
print("현재 수집 진행 페이지 확인")
print("=" * 60)
print()

# 1. 현재 저장된 데이터 수
try:
    result = supabase.table("library_items").select("*", count="exact").execute()
    total_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
    print(f"✅ 현재 저장된 도서 수: {total_count:,}권")
except Exception as e:
    print(f"❌ 데이터 확인 중 오류: {e}")
    total_count = 0

print()

# 2. 최근 수집된 데이터 확인 (created_at 기준)
try:
    recent_data = supabase.table("library_items")\
        .select("created_at")\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()
    
    if recent_data.data:
        latest_time = recent_data.data[0].get("created_at")
        print(f"최근 수집 시간: {latest_time}")
except Exception as e:
    print(f"최근 수집 시간 확인 중 오류: {e}")

print()

# 3. API에서 페이지별로 확인하여 어느 페이지까지 데이터가 있는지 확인
print("=" * 60)
print("API 페이지별 데이터 확인 중...")
print("=" * 60)
print()

url = "http://data4library.kr/api/itemSrch"

# 이진 탐색으로 마지막 페이지 찾기
def find_last_page_with_data(start_page, end_page):
    """이진 탐색으로 데이터가 있는 마지막 페이지 찾기"""
    last_valid_page = start_page
    
    while start_page <= end_page:
        mid_page = (start_page + end_page) // 2
        
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": PANGYO_CODE,
            "startDt": "2010-01-01",
            "endDt": "2025-12-31",
            "pageNo": mid_page,
            "pageSize": 100,
            "format": "json"
        }
        
        try:
            res = requests.get(url, params=params, timeout=60)
            if res.status_code == 200:
                data = res.json()
                docs = data.get("response", {}).get("docs", [])
                
                if docs:
                    # 아동 도서 개수 확인
                    child_count = 0
                    for d in docs:
                        item = d.get("doc", {})
                        call_numbers = item.get("callNumbers", [])
                        
                        for call_info in call_numbers:
                            call_number = call_info.get("callNumber", {})
                            separate_shelf_name = call_number.get("separate_shelf_name", "")
                            shelf_loc_name = call_number.get("shelf_loc_name", "")
                            
                            if (separate_shelf_name and (separate_shelf_name.startswith('아') or separate_shelf_name.startswith('유'))) or \
                               ('어린이' in shelf_loc_name):
                                child_count += 1
                                break
                    
                    if child_count > 0:
                        print(f"  페이지 {mid_page}: 데이터 있음 (아동 도서 {child_count}권)")
                        last_valid_page = mid_page
                        start_page = mid_page + 1
                    else:
                        print(f"  페이지 {mid_page}: 아동 도서 없음")
                        end_page = mid_page - 1
                else:
                    print(f"  페이지 {mid_page}: 데이터 없음")
                    end_page = mid_page - 1
            else:
                print(f"  페이지 {mid_page}: API 오류 ({res.status_code})")
                end_page = mid_page - 1
        except Exception as e:
            print(f"  페이지 {mid_page} 확인 중 오류: {e}")
            end_page = mid_page - 1
    
    return last_valid_page

# 현재까지 수집된 것으로 추정되는 페이지 범위 확인
# 33,174권이면, 페이지당 약 100권씩 수집했다고 가정하면 약 332페이지
# 하지만 실제로는 아동 도서만 필터링하므로 더 많은 페이지를 확인했을 것

print("페이지 범위 확인 중...")
print()

# 1단계: 대략적인 범위 확인
test_pages = [300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500]

last_page_with_data = 0
first_empty_page = None

for test_page in test_pages:
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "startDt": "2010-01-01",
        "endDt": "2025-12-31",
        "pageNo": test_page,
        "pageSize": 100,
        "format": "json"
    }
    
    try:
        res = requests.get(url, params=params, timeout=60)
        if res.status_code == 200:
            data = res.json()
            docs = data.get("response", {}).get("docs", [])
            
            if docs:
                # 아동 도서 개수 확인
                child_count = 0
                for d in docs:
                    item = d.get("doc", {})
                    call_numbers = item.get("callNumbers", [])
                    
                    for call_info in call_numbers:
                        call_number = call_info.get("callNumber", {})
                        separate_shelf_name = call_number.get("separate_shelf_name", "")
                        shelf_loc_name = call_number.get("shelf_loc_name", "")
                        
                        if (separate_shelf_name and (separate_shelf_name.startswith('아') or separate_shelf_name.startswith('유'))) or \
                           ('어린이' in shelf_loc_name):
                            child_count += 1
                            break
                
                if child_count > 0:
                    print(f"✅ 페이지 {test_page}: 데이터 있음 (아동 도서 {child_count}권)")
                    last_page_with_data = test_page
                else:
                    print(f"⚠️  페이지 {test_page}: 아동 도서 없음")
                    if first_empty_page is None:
                        first_empty_page = test_page
            else:
                print(f"❌ 페이지 {test_page}: 데이터 없음 (끝)")
                if first_empty_page is None:
                    first_empty_page = test_page
                break
        else:
            print(f"⚠️  페이지 {test_page}: API 오류 ({res.status_code})")
    except Exception as e:
        print(f"⚠️  페이지 {test_page} 확인 중 오류: {e}")

print()
print("=" * 60)
print("결론:")
print("-" * 60)
print(f"현재 저장된 도서: {total_count:,}권")
print(f"데이터가 있는 마지막 페이지: {last_page_with_data}페이지")
if first_empty_page:
    print(f"데이터가 없는 첫 페이지: {first_empty_page}페이지")
    print(f"추정 수집 완료 페이지: {first_empty_page - 1}페이지")
else:
    print("더 확인이 필요합니다.")

print()
print("=" * 60)



