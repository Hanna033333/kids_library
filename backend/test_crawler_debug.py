import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment (.env)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DATA4LIBRARY_KEY = os.getenv("DATA4LIBRARY_KEY")
PANGYO_CODE = "141231"

print(f"API Key 존재 여부: {DATA4LIBRARY_KEY is not None}")
print(f"도서관 코드: {PANGYO_CODE}")

# API 테스트
url = "http://data4library.kr/api/itemSrch"
# 여러 날짜 형식 테스트
test_cases = [
    {"startDt": "20240101", "endDt": "20241231", "name": "YYYYMMDD 형식"},
    {"startDt": "2020-01-01", "endDt": "2025-12-31", "name": "YYYY-MM-DD 형식"},
    {"startDt": "20200101", "endDt": "20251231", "name": "더 넓은 범위 YYYYMMDD"},
]

for test_case in test_cases:
    print(f"\n{'='*60}")
    print(f"테스트: {test_case['name']}")
    print(f"{'='*60}")
    
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "startDt": test_case["startDt"],
        "endDt": test_case["endDt"],
        "pageNo": 1,
        "pageSize": 10,
        "format": "json"
    }
    
    print(f"요청 파라미터: {params}")
    
    try:
        res = requests.get(url, params=params, timeout=60)
        print(f"응답 상태 코드: {res.status_code}")
        data = res.json()
        
        if isinstance(data, dict):
            response = data.get("response", {})
            
            if isinstance(response, dict):
                # 에러 확인
                if "error" in response:
                    error_msg = response.get("error", {})
                    print(f"⚠️ 에러: {error_msg}")
                else:
                    numFound = response.get("numFound", 0)
                    docs = response.get("docs", [])
                    print(f"✅ 성공! 총 검색 결과: {numFound}건, 현재 페이지: {len(docs)}건")
                    if docs:
                        print(f"   첫 번째 문서: {docs[0].get('doc', {}).get('bookname', 'N/A')}")
                    break  # 성공하면 중단
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

print(f"\nAPI 요청 URL: {url}")
print(f"요청 파라미터: {params}")

try:
    res = requests.get(url, params=params, timeout=60)
    print(f"\n응답 상태 코드: {res.status_code}")
    data = res.json()
    print(f"응답 데이터 키: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
    
    if isinstance(data, dict):
        response = data.get("response", {})
        print(f"Response 키: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
        
        if isinstance(response, dict):
            # 에러 확인
            if "error" in response:
                error_msg = response.get("error", {})
                print(f"\n⚠️ 에러 발생:")
                print(f"  에러 내용: {error_msg}")
            
            numFound = response.get("numFound", 0)
            docs = response.get("docs", [])
            print(f"\n총 검색 결과: {numFound}건")
            print(f"현재 페이지 문서 수: {len(docs)}건")
            
            if docs:
                print(f"\n첫 번째 문서 샘플:")
                first_doc = docs[0].get("doc", {})
                print(f"  - 제목: {first_doc.get('bookname', 'N/A')}")
                print(f"  - 분류번호: {first_doc.get('class_no', 'N/A')}")
                print(f"  - ISBN13: {first_doc.get('isbn13', 'N/A')}")
                
                # 분류번호 분석
                class_no = first_doc.get('class_no', '')
                if class_no:
                    try:
                        prefix = int(class_no.split('.')[0])
                        print(f"  - 분류번호 접두사: {prefix} (아동도서 여부: {0 <= prefix <= 99})")
                    except:
                        print(f"  - 분류번호 파싱 실패")
except Exception as e:
    print(f"\n오류 발생: {e}")
    import traceback
    traceback.print_exc()

