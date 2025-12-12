"""
수집 진행 상황 상세 확인
"""
from supabase_client import supabase
from crawler import DATA4LIBRARY_KEY, PANGYO_CODE
import requests

print("=" * 60)
print("수집 진행 상황 상세 확인")
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

# 2. API에서 전체 데이터 수 확인
print("API에서 전체 아동 도서 수 확인 중...")
print("-" * 60)

try:
    url = "http://data4library.kr/api/itemSrch"
    
    # 전체 기간 (2010-2025) 확인
    params_all = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "startDt": "2010-01-01",
        "endDt": "2025-12-31",
        "pageNo": 1,
        "pageSize": 1,
        "format": "json"
    }
    
    response = requests.get(url, params=params_all, timeout=60)
    if response.status_code == 200:
        data = response.json()
        
        # 응답 구조 확인
        response_data = data.get("response", {})
        
        # docs 구조 확인
        docs = response_data.get("docs", [])
        if docs:
            first_doc = docs[0].get("doc", {})
            print(f"샘플 도서: {first_doc.get('bookname', 'N/A')}")
            print(f"출판년도: {first_doc.get('publication_year', 'N/A')}")
        
        # 전체 수 확인을 위해 여러 페이지 확인
        # 실제로는 페이지를 계속 요청해서 전체 수를 확인해야 함
        # 하지만 시간이 오래 걸리므로 추정치 사용
        
        print("\n페이지별 데이터 수 확인 중...")
        
        # 첫 페이지 확인
        params_page1 = params_all.copy()
        params_page1["pageSize"] = 100
        response_page1 = requests.get(url, params=params_page1, timeout=60)
        if response_page1.status_code == 200:
            data_page1 = response_page1.json()
            docs_page1 = data_page1.get("response", {}).get("docs", [])
            
            # 아동 도서만 필터링
            child_books_count = 0
            for d in docs_page1:
                item = d.get("doc", {})
                call_numbers = item.get("callNumbers", [])
                is_child = False
                
                for call_info in call_numbers:
                    call_number = call_info.get("callNumber", {})
                    separate_shelf_name = call_number.get("separate_shelf_name", "")
                    shelf_loc_name = call_number.get("shelf_loc_name", "")
                    
                    if (separate_shelf_name and (separate_shelf_name.startswith('아') or separate_shelf_name.startswith('유'))) or \
                       ('어린이' in shelf_loc_name):
                        is_child = True
                        break
                
                if is_child:
                    child_books_count += 1
            
            print(f"첫 페이지(100권) 중 아동 도서: {child_books_count}권")
            print(f"아동 도서 비율: {child_books_count / len(docs_page1) * 100:.1f}%")
            
            # 전체 페이지 수 추정 (현재까지 459페이지 수집됨)
            # 페이지당 평균 아동 도서 수 추정
            avg_child_per_page = child_books_count
            
            # 현재까지 수집된 페이지 수
            pages_collected = 459
            
            # 현재까지 수집된 도서 수
            estimated_collected = pages_collected * avg_child_per_page
            
            print(f"\n📊 추정치:")
            print(f"   페이지당 평균 아동 도서: {avg_child_per_page}권")
            print(f"   수집된 페이지: {pages_collected}페이지")
            print(f"   추정 수집 도서 수: {estimated_collected:,}권")
            print(f"   실제 저장된 도서 수: {total_count:,}권")
            
            # 전체 페이지 수 추정 (API가 정렬 순서에 따라 다를 수 있음)
            # 실제로는 더 많은 페이지가 있을 수 있음
            estimated_total_pages = 2000  # 보수적 추정
            estimated_total_books = estimated_total_pages * avg_child_per_page
            
            print(f"\n📈 진행률 추정:")
            print(f"   예상 전체 페이지: {estimated_total_pages}페이지 (추정)")
            print(f"   예상 전체 아동 도서: {estimated_total_books:,}권 (추정)")
            print(f"   현재 진행률: {pages_collected / estimated_total_pages * 100:.1f}% (추정)")
            print(f"   남은 페이지: 약 {estimated_total_pages - pages_collected}페이지")
            print(f"   남은 도서: 약 {estimated_total_books - total_count:,}권 (추정)")
            
    else:
        print(f"❌ API 요청 실패: {response.status_code}")
        
except Exception as e:
    print(f"❌ API 확인 중 오류: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("참고:")
print("- API는 날짜 순서가 아닐 수 있습니다.")
print("- 정확한 진행률은 API 전체 데이터를 확인해야 합니다.")
print("- 현재 스크립트는 2010-01-01 ~ 2025-12-31 전체 기간을 수집합니다.")
print("=" * 60)





