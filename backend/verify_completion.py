"""
수집 완료 확인 - 더 이상 수집할 데이터가 있는지 확인
"""
from supabase_client import supabase
from crawler import DATA4LIBRARY_KEY, PANGYO_CODE
import requests

print("=" * 60)
print("수집 완료 확인")
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

# 마지막으로 확인된 페이지 이후에 더 데이터가 있는지 확인
print("=" * 60)
print("추가 데이터 확인 중...")
print("=" * 60)
print()

url = "http://data4library.kr/api/itemSrch"

# 1061페이지 이후 확인
test_pages = [1061, 1065, 1070, 1080, 1100, 1200, 1300, 1400, 1500]

has_more_data = False
last_page_with_data = 1061

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
                    print(f"✅ 페이지 {test_page}: 아동 도서 {child_count}권 있음")
                    has_more_data = True
                    last_page_with_data = test_page
                else:
                    print(f"⚠️  페이지 {test_page}: 아동 도서 없음")
            else:
                print(f"❌ 페이지 {test_page}: 데이터 없음")
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
print(f"마지막으로 확인된 페이지: {last_page_with_data}페이지")

if has_more_data:
    print()
    print("⚠️  더 수집할 데이터가 있습니다!")
    print(f"   {last_page_with_data + 1}페이지부터 계속 수집하세요.")
else:
    print()
    print("✅ 수집이 완료된 것으로 보입니다!")
    print("   1061페이지 이후 더 이상 아동 도서 데이터가 없습니다.")

print("=" * 60)



