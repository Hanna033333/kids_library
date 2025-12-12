"""
실제로 어느 페이지까지 수집되었는지 확인
- API에서 각 페이지를 확인하여 이미 저장된 데이터와 비교
"""
from supabase_client import supabase
from crawler import DATA4LIBRARY_KEY, PANGYO_CODE
import requests

print("=" * 60)
print("실제 수집된 마지막 페이지 확인")
print("=" * 60)
print()

# 현재 저장된 데이터 수
try:
    result = supabase.table("library_items").select("*", count="exact").execute()
    total_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
    print(f"현재 저장된 도서 수: {total_count:,}권")
except Exception as e:
    print(f"데이터 확인 중 오류: {e}")
    total_count = 0

print()

# 몇 개의 ISBN을 샘플로 가져와서 API에서 어느 페이지에 있는지 확인
try:
    # 저장된 데이터 중 일부 ISBN 가져오기
    sample_data = supabase.table("library_items")\
        .select("isbn13, title, callno")\
        .limit(10)\
        .execute()
    
    if sample_data.data:
        print(f"샘플 데이터 {len(sample_data.data)}개 확인 중...")
        print()
        
        # 각 샘플이 API의 어느 페이지에 있는지 확인
        url = "http://data4library.kr/api/itemSrch"
        
        for sample in sample_data.data[:3]:  # 처음 3개만 확인
            isbn = sample.get("isbn13")
            title = sample.get("title")
            
            if not isbn:
                continue
            
            # ISBN으로 검색하여 페이지 찾기
            # 직접 페이지를 찾기는 어려우므로, 대략적인 범위만 확인
            print(f"  - {title[:30]}... (ISBN: {isbn[:13]})")
except Exception as e:
    print(f"샘플 데이터 확인 중 오류: {e}")

print()

# 더 간단한 방법: 페이지를 역순으로 확인하여 데이터가 있는 마지막 페이지 찾기
print("=" * 60)
print("데이터가 있는 마지막 페이지 찾기 (역순 확인)...")
print("=" * 60)
print()

url = "http://data4library.kr/api/itemSrch"

# 1000페이지부터 역순으로 확인
for test_page in range(1000, 400, -50):  # 50페이지씩 건너뛰며 확인
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
                    # 이 페이지 근처에서 더 정확히 확인
                    print(f"   → {test_page}~{test_page+50} 페이지 범위에 데이터 있음")
                    break
            else:
                print(f"❌ 페이지 {test_page}: 데이터 없음")
    except Exception as e:
        print(f"⚠️  페이지 {test_page} 확인 중 오류: {e}")

print()
print("=" * 60)
print("결론:")
print("-" * 60)
print("스크립트는 460페이지부터 시작하도록 설정되어 있습니다.")
print("하지만 실제로는 더 많은 페이지를 수집했을 수 있습니다.")
print()
print("다음 단계:")
print("1. 460페이지부터 계속 수집 (중복은 upsert로 자동 처리)")
print("2. 또는 마지막으로 확인된 페이지부터 시작")
print("=" * 60)



