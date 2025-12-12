"""
최종 수집 상태 확인 및 남은 데이터 확인
"""
from supabase_client import supabase
from crawler import DATA4LIBRARY_KEY, PANGYO_CODE
import requests

print("=" * 60)
print("수집 최종 상태 확인")
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

# 2. 어제와 비교
yesterday_count = 15525
added_today = total_count - yesterday_count
print(f"어제 완료: {yesterday_count:,}권")
print(f"오늘 추가: +{added_today:,}권")
print(f"총 누적: {total_count:,}권")
print()

# 3. API에서 더 수집할 데이터가 있는지 확인
print("=" * 60)
print("남은 데이터 확인 중...")
print("=" * 60)
print()

try:
    url = "http://data4library.kr/api/itemSrch"
    
    # 높은 페이지 번호로 확인 (예: 1000페이지)
    test_pages = [1000, 1500, 2000]
    
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
                    
                    print(f"{test_page} 페이지: 데이터 있음 (아동 도서 {child_count}권)")
                else:
                    print(f"{test_page} 페이지: 데이터 없음 (끝)")
                    break
            else:
                print(f"{test_page} 페이지: API 오류 ({res.status_code})")
        except Exception as e:
            print(f"{test_page} 페이지 확인 중 오류: {e}")
            break
    
    print()
    print("=" * 60)
    print("결론:")
    print("-" * 60)
    
    if total_count >= 30000:
        print(f"✅ 현재 {total_count:,}권이 수집되었습니다.")
        print("예상 전체 아동 도서: 약 62,000권 (추정)")
        print(f"진행률: 약 {total_count / 62000 * 100:.1f}%")
        print()
        print("더 수집할 데이터가 있는지 확인하려면")
        print("스크립트를 계속 실행하거나, API 응답을 확인해야 합니다.")
    
except Exception as e:
    print(f"API 확인 중 오류: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)




