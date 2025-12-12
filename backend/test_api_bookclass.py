"""
data4library API에 bookClass 파라미터가 있는지 테스트
"""
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DATA4LIBRARY_KEY = os.getenv("DATA4LIBRARY_KEY")
PANGYO_CODE = "141231"

url = "http://data4library.kr/api/itemSrch"

print("=" * 60)
print("API bookClass 파라미터 테스트")
print("=" * 60)
print()

# 테스트할 bookClass 값들
test_values = ["CHILD", "아동", "child", "CHILDREN", "아동도서"]

for book_class in test_values:
    print(f"\n{'='*60}")
    print(f"테스트: bookClass={book_class}")
    print(f"{'='*60}")
    
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "startDt": "2024-12-01",
        "endDt": "2024-12-31",
        "pageNo": 1,
        "pageSize": 10,
        "format": "json",
        "bookClass": book_class
    }
    
    try:
        res = requests.get(url, params=params, timeout=30)
        print(f"응답 상태 코드: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            
            # 에러 확인
            if "error" in data.get("response", {}):
                error_msg = data["response"]["error"]
                print(f"⚠️ 에러: {error_msg}")
            else:
                docs = data.get("response", {}).get("docs", [])
                numFound = data.get("response", {}).get("numFound", 0)
                
                print(f"✅ 성공!")
                print(f"   총 검색 결과: {numFound}건")
                print(f"   현재 페이지: {len(docs)}건")
                
                if docs:
                    print(f"\n   첫 번째 도서 샘플:")
                    first_doc = docs[0].get("doc", {})
                    print(f"   - 제목: {first_doc.get('bookname', 'N/A')}")
                    print(f"   - 청구기호: {first_doc.get('class_no', 'N/A')}")
                    print(f"   - ISBN: {first_doc.get('isbn13', 'N/A')}")
                    
                    # 청구기호가 '아'나 '유'로 시작하는지 확인
                    callno = first_doc.get('class_no', '')
                    if callno:
                        if callno.startswith('아') or callno.startswith('유'):
                            print(f"   ✅ 청구기호가 '아' 또는 '유'로 시작함!")
                        else:
                            print(f"   ⚠️ 청구기호가 '아'/'유'로 시작하지 않음")
                    
                    # 여러 샘플 확인
                    print(f"\n   처음 5개 도서의 청구기호:")
                    for i, doc in enumerate(docs[:5], 1):
                        doc_item = doc.get("doc", {})
                        callno = doc_item.get('class_no', 'N/A')
                        title = doc_item.get('bookname', 'N/A')
                        print(f"   {i}. {callno} - {title[:30]}")
                
                # 이 값이 작동하면 중단
                if numFound > 0:
                    print(f"\n✅ bookClass='{book_class}' 파라미터가 작동합니다!")
                    break
        else:
            print(f"❌ HTTP 오류: {res.status_code}")
            print(f"응답: {res.text[:200]}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*60}")
print("테스트 완료")
print(f"{'='*60}")






