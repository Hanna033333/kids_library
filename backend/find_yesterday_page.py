"""
어제 몇 페이지까지 진행했는지 확인
- 저장된 데이터 수를 기준으로 추정
- 페이지당 평균 아동 도서 수를 계산하여 추정
"""
from supabase_client import supabase
from crawler import DATA4LIBRARY_KEY, PANGYO_CODE
import requests

print("=" * 60)
print("어제 진행된 마지막 페이지 확인")
print("=" * 60)
print()

# 현재 저장된 데이터 수
try:
    result = supabase.table("library_items").select("*", count="exact").execute()
    total_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
    print(f"✅ 현재 저장된 도서 수: {total_count:,}권")
except Exception as e:
    print(f"❌ 데이터 확인 중 오류: {e}")
    total_count = 0

print()

# 페이지당 평균 아동 도서 수를 계산하기 위해 샘플 페이지 확인
print("=" * 60)
print("페이지당 평균 아동 도서 수 계산 중...")
print("=" * 60)
print()

url = "http://data4library.kr/api/itemSrch"

# 여러 페이지를 샘플로 확인하여 평균 계산
sample_pages = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
total_child_books = 0
valid_pages = 0

for test_page in sample_pages:
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
                    total_child_books += child_count
                    valid_pages += 1
                    print(f"  페이지 {test_page}: 아동 도서 {child_count}권")
            else:
                print(f"  페이지 {test_page}: 데이터 없음")
                break
        else:
            print(f"  페이지 {test_page}: API 오류 ({res.status_code})")
    except Exception as e:
        print(f"  페이지 {test_page} 확인 중 오류: {e}")

print()

if valid_pages > 0:
    avg_per_page = total_child_books / valid_pages
    print(f"페이지당 평균 아동 도서 수: {avg_per_page:.1f}권")
    print()
    
    # 저장된 데이터 수를 기준으로 추정 페이지 계산
    estimated_page = int(total_count / avg_per_page)
    print("=" * 60)
    print("추정 결과:")
    print("-" * 60)
    print(f"현재 저장된 도서: {total_count:,}권")
    print(f"페이지당 평균: {avg_per_page:.1f}권")
    print(f"추정 진행 페이지: 약 {estimated_page}페이지")
    print()
    print(f"✅ 다음 수집 시작 페이지: {estimated_page + 1}페이지")
    print("=" * 60)
else:
    print("⚠️  샘플 페이지에서 데이터를 찾을 수 없습니다.")
    print("기본값으로 460페이지부터 시작합니다.")



