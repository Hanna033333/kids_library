"""
다양한 파라미터 이름으로 아동 도서 필터링 테스트
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
print("다양한 파라미터 이름 테스트")
print("=" * 60)
print()

# 기본 요청 (비교용)
base_params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": "2024-12-01",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 10,
    "format": "json"
}

res_base = requests.get(url, params=base_params, timeout=30)
data_base = res_base.json()
numFound_base = data_base.get("response", {}).get("numFound", 0)
print(f"기본 요청 (파라미터 없음): {numFound_base}건")
print()

# 테스트할 파라미터들
test_params_list = [
    {"bookClass": "CHILD"},
    {"bookClass": "아동"},
    {"bookClass": "child"},
    {"bookType": "CHILD"},
    {"bookType": "아동"},
    {"type": "CHILD"},
    {"type": "아동"},
    {"category": "CHILD"},
    {"category": "아동"},
    {"bookCategory": "CHILD"},
    {"bookCategory": "아동"},
    {"searchBookClass": "CHILD"},
    {"searchBookClass": "아동"},
]

for test_params in test_params_list:
    param_name = list(test_params.keys())[0]
    param_value = test_params[param_name]
    
    params = {**base_params, **test_params}
    
    try:
        res = requests.get(url, params=params, timeout=30)
        if res.status_code == 200:
            data = res.json()
            numFound = data.get("response", {}).get("numFound", 0)
            
            # 결과가 다르면 표시
            if numFound != numFound_base:
                print(f"✅ {param_name}={param_value}: {numFound}건 (차이: {numFound_base - numFound}건)")
                
                # 샘플 확인
                docs = data.get("response", {}).get("docs", [])
                if docs:
                    first_doc = docs[0].get("doc", {})
                    callno = first_doc.get("class_no", "")
                    title = first_doc.get("bookname", "")
                    print(f"   샘플: {callno} - {title[:40]}")
            else:
                print(f"   {param_name}={param_value}: {numFound}건 (동일)")
    except Exception as e:
        print(f"   {param_name}={param_value}: 오류 - {e}")

print()
print("=" * 60)
print("테스트 완료")
print("=" * 60)






