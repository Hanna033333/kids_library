import requests
from core.config import DATA4LIBRARY_KEY
import json

PANGYO_LIB_CODE = "141231"

def test_libsrchbybook():
    """libSrchByBook API 테스트 - 도서관별 장서 소장 확인"""
    
    test_isbn = "9788949110066"  # 별별 수사대 보리스
    
    url = "http://data4library.kr/api/libSrchByBook"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "isbn": test_isbn,
        "pageNo": 1,
        "pageSize": 100,
        "format": "json"
    }
    
    print(f"Testing libSrchByBook API")
    print(f"ISBN: {test_isbn}")
    print(f"URL: {url}")
    print()
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Full URL: {response.url}")
        print()
        
        data = response.json()
        
        # 전체 응답을 파일에 저장
        with open("libsrchbybook_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("Response saved to libsrchbybook_response.json")
        
        # 응답 파싱
        response_obj = data.get("response", {})
        libs = response_obj.get("libs", [])
        
        print(f"\nLibraries found: {len(libs) if isinstance(libs, list) else 1}")
        
        # 판교 도서관 찾기
        if isinstance(libs, list):
            for lib_data in libs:
                lib = lib_data.get("lib", {})
                lib_code = lib.get("libCode")
                lib_name = lib.get("libName")
                
                print(f"\n도서관: {lib_name} ({lib_code})")
                
                if lib_code == PANGYO_LIB_CODE:
                    print("  ✅ 판교 도서관 발견!")
                    
                    # book 데이터 확인
                    books = lib_data.get("book", [])
                    if not isinstance(books, list):
                        books = [books] if books else []
                    
                    print(f"  책 개수: {len(books)}")
                    
                    for idx, book in enumerate(books):
                        print(f"\n  [{idx+1}]")
                        print(f"    - vol: {book.get('vol', 'N/A')}")
                        print(f"    - class_no: {book.get('class_no', 'N/A')}")
                        print(f"    - bookname: {book.get('bookname', 'N/A')}")
                        print(f"    - loan_cnt: {book.get('loan_cnt', 'N/A')}")
        else:
            print("\nNo libraries found or unexpected format")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_libsrchbybook()
