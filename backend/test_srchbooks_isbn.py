import requests
from core.config import DATA4LIBRARY_KEY
import json

PANGYO_LIB_CODE = "141231"

def test_srchbooks():
    """srchBooks API 테스트"""
    
    test_isbn = "9788949110066"  # 별별 수사대 보리스
    
    url = "http://data4library.kr/api/srchBooks"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "isbn13": test_isbn,
        "format": "json"
    }
    
    print(f"Testing srchBooks API")
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
        with open("srchbooks_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("Response saved to srchbooks_response.json")
        
        # 응답 파싱
        response_obj = data.get("response", {})
        
        # 에러 확인
        if "error" in response_obj:
            print(f"\n❌ Error: {response_obj['error']}")
            return
        
        docs = response_obj.get("docs", [])
        
        print(f"\nDocs count: {len(docs)}")
        
        if docs:
            print("\n✅ Results found!")
            for idx, doc_wrapper in enumerate(docs):
                doc = doc_wrapper.get("doc", {})
                print(f"\n[{idx+1}]")
                print(f"  - bookname: {doc.get('bookname', 'N/A')}")
                print(f"  - isbn13: {doc.get('isbn13', 'N/A')}")
                print(f"  - vol: {doc.get('vol', 'N/A')}")
                print(f"  - class_no: {doc.get('class_no', 'N/A')}")
                
                # callNumbers 확인
                call_numbers = doc.get('callNumbers', [])
                if call_numbers:
                    for cn_wrapper in call_numbers:
                        cn = cn_wrapper.get('callNumber', {})
                        separate_shelf = cn.get('separate_shelf_code', '')
                        book_code = cn.get('book_code', '')
                        full_callno = f"{separate_shelf} {cn.get('class_no', '')}-{book_code}".strip()
                        print(f"  - full_callno: {full_callno}")
        else:
            print("\n❌ No results found")
            print("\nFull response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_srchbooks()
