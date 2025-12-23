import requests
from core.config import DATA4LIBRARY_KEY
import json

PANGYO_LIB_CODE = "141231"

def test_itemsrch_simple():
    """itemSrch API 간단 테스트"""
    
    test_isbn = "9788949110066"  # 별별 수사대 보리스
    
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "type": "isbn",
        "keyword": test_isbn,
        "startDt": "2000-01-01",
        "endDt": "2025-12-31",
        "format": "json"
    }
    
    print(f"Testing ISBN: {test_isbn}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print()
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Full URL: {response.url}")
        print()
        
        data = response.json()
        
        # 전체 응답을 파일에 저장
        with open("itemsrch_test_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("Response saved to itemsrch_test_response.json")
        
        # 기본 정보 출력
        response_obj = data.get("response", {})
        docs = response_obj.get("docs", [])
        
        print(f"\nDocs count: {len(docs)}")
        
        if docs:
            print("\nFirst doc:")
            print(json.dumps(docs[0], indent=2, ensure_ascii=False))
        else:
            print("\nNo docs found. Full response:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_itemsrch_simple()
