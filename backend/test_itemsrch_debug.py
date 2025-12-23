import requests
from core.config import DATA4LIBRARY_KEY
import json

PANGYO_LIB_CODE = "141231"

def test_itemsrch_variations():
    """itemSrch API 다양한 파라미터 조합 테스트"""
    
    # 테스트용 ISBN (중복 청구기호 중 하나)
    test_isbn = "9788949110066"  # 별별 수사대 보리스
    
    print("=" * 80)
    print(f"📚 itemSrch API 파라미터 테스트 - ISBN: {test_isbn}")
    print("=" * 80)
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "기본 (type=isbn, 소문자)",
            "params": {
                "authKey": DATA4LIBRARY_KEY,
                "libCode": PANGYO_LIB_CODE,
                "type": "isbn",
                "keyword": test_isbn,
                "format": "json"
            }
        },
        {
            "name": "type=ISBN (대문자)",
            "params": {
                "authKey": DATA4LIBRARY_KEY,
                "libCode": PANGYO_LIB_CODE,
                "type": "ISBN",
                "keyword": test_isbn,
                "format": "json"
            }
        },
        {
            "name": "isbn13 파라미터 사용",
            "params": {
                "authKey": DATA4LIBRARY_KEY,
                "libCode": PANGYO_LIB_CODE,
                "isbn13": test_isbn,
                "format": "json"
            }
        },
        {
            "name": "날짜 범위 추가",
            "params": {
                "authKey": DATA4LIBRARY_KEY,
                "libCode": PANGYO_LIB_CODE,
                "type": "isbn",
                "keyword": test_isbn,
                "startDt": "2000-01-01",
                "endDt": "2025-12-22",
                "format": "json"
            }
        },
        {
            "name": "pageNo, pageSize 추가",
            "params": {
                "authKey": DATA4LIBRARY_KEY,
                "libCode": PANGYO_LIB_CODE,
                "type": "isbn",
                "keyword": test_isbn,
                "pageNo": "1",
                "pageSize": "100",
                "format": "json"
            }
        }
    ]
    
    url = "http://data4library.kr/api/itemSrch"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[테스트 {i}] {test_case['name']}")
        print("-" * 80)
        
        try:
            response = requests.get(url, params=test_case['params'], timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"URL: {response.url}")
            
            data = response.json()
            
            # 응답 구조 확인
            response_obj = data.get("response", {})
            docs = response_obj.get("docs", [])
            
            print(f"결과 개수: {len(docs)}")
            
            if docs:
                print("\n✅ 결과 발견!")
                for idx, doc_wrapper in enumerate(docs[:3]):  # 최대 3개만 출력
                    doc = doc_wrapper.get("doc", {})
                    print(f"\n  [{idx+1}]")
                    print(f"    - vol: {doc.get('vol', 'N/A')}")
                    print(f"    - class_no: {doc.get('class_no', 'N/A')}")
                    print(f"    - bookname: {doc.get('bookname', 'N/A')}")
                    print(f"    - isbn13: {doc.get('isbn13', 'N/A')}")
            else:
                print("❌ 결과 없음")
                # 전체 응답 출력
                print("\n전체 응답:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
        except Exception as e:
            print(f"❌ 에러: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_itemsrch_variations()
