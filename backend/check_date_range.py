"""
수집된 데이터의 날짜 범위 확인
"""
from supabase_client import supabase
from crawler import fetch_library_books_child, DATA4LIBRARY_KEY, PANGYO_CODE
import requests
from datetime import datetime

print("=" * 60)
print("수집된 데이터 날짜 범위 확인")
print("=" * 60)
print()

# 1. 현재 저장된 데이터 수 확인
try:
    result = supabase.table("library_items").select("*", count="exact").execute()
    total_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
    print(f"현재 저장된 도서 수: {total_count}권")
except Exception as e:
    print(f"데이터 확인 중 오류: {e}")
    total_count = 0

print()

# 2. API에서 전체 데이터 수 확인 (2010-2025)
print("API에서 전체 데이터 수 확인 중...")
print("-" * 60)

try:
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "startDt": "2010-01-01",
        "endDt": "2025-12-31",
        "pageNo": 1,
        "pageSize": 1,  # 첫 페이지만 확인
        "format": "json"
    }
    
    response = requests.get(url, params=params, timeout=60)
    if response.status_code == 200:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        if docs:
            # 전체 데이터 수 확인을 위해 numFound 확인
            # API 응답 구조 확인
            result_info = data.get("response", {}).get("result", {})
            if result_info:
                total_api_count = result_info.get("numFound", 0)
                print(f"API 전체 아동 도서 수 (2010-2025): {total_api_count}권")
            else:
                print("API 응답에서 전체 수를 확인할 수 없습니다.")
                print("페이지별로 확인합니다...")
                
                # 첫 페이지와 마지막 페이지 확인
                # 최신 데이터 확인
                params_recent = params.copy()
                params_recent["startDt"] = "2024-01-01"
                params_recent["endDt"] = "2025-12-31"
                response_recent = requests.get(url, params=params_recent, timeout=60)
                if response_recent.status_code == 200:
                    data_recent = response_recent.json()
                    docs_recent = data_recent.get("response", {}).get("docs", [])
                    if docs_recent:
                        first_item = docs_recent[0].get("doc", {})
                        print(f"최신 도서: {first_item.get('bookname', 'N/A')}")
                        # 날짜 정보 확인
                        if 'publication_date' in first_item:
                            print(f"출판일: {first_item.get('publication_date', 'N/A')}")
                        if 'publication_year' in first_item:
                            print(f"출판년도: {first_item.get('publication_year', 'N/A')}")
                
                # 오래된 데이터 확인
                params_old = params.copy()
                params_old["startDt"] = "2010-01-01"
                params_old["endDt"] = "2011-12-31"
                response_old = requests.get(url, params=params_old, timeout=60)
                if response_old.status_code == 200:
                    data_old = response_old.json()
                    docs_old = data_old.get("response", {}).get("docs", [])
                    if docs_old:
                        first_item_old = docs_old[0].get("doc", {})
                        print(f"오래된 도서: {first_item_old.get('bookname', 'N/A')}")
                        if 'publication_date' in first_item_old:
                            print(f"출판일: {first_item_old.get('publication_date', 'N/A')}")
                        if 'publication_year' in first_item_old:
                            print(f"출판년도: {first_item_old.get('publication_year', 'N/A')}")
        else:
            print("API 응답에 데이터가 없습니다.")
    else:
        print(f"API 요청 실패: {response.status_code}")
        
except Exception as e:
    print(f"API 확인 중 오류: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)

# 3. 수집 진행률 추정
print("수집 진행률 추정:")
print("-" * 60)

# API에서 페이지별로 확인
try:
    # 현재까지 수집된 페이지 수 추정 (459페이지까지 완료)
    pages_collected = 459
    books_per_page = 100  # 페이지 크기
    
    # 아동 도서 비율 추정 (전체 중 일부만 아동 도서)
    # 실제로는 페이지당 평균 20-30권 정도 수집되는 것으로 보임
    estimated_total_pages = 2000  # 추정치 (실제로는 더 많을 수 있음)
    
    print(f"수집된 페이지 수: {pages_collected}페이지")
    print(f"수집된 도서 수: {total_count}권")
    print(f"예상 진행률: {pages_collected / estimated_total_pages * 100:.1f}% (추정)")
    print()
    print("⚠️  정확한 진행률은 API 전체 데이터 수를 확인해야 합니다.")
    
except Exception as e:
    print(f"진행률 계산 중 오류: {e}")

print()
print("=" * 60)
print("참고: API는 날짜 범위(2010-2025)로 필터링하지만,")
print("실제 수집은 페이지 단위로 진행되므로 정확한 날짜 범위는 확인하기 어렵습니다.")
print("=" * 60)





