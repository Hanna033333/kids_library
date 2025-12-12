"""
data4library API 응답에서 청구기호 형식 확인
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

params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": "2024-01-01",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 100,
    "format": "json"
}

print("=" * 60)
print("data4library API 응답에서 청구기호 형식 확인")
print("=" * 60)
print()

res = requests.get(url, params=params, timeout=30)
data = res.json()
docs = data.get("response", {}).get("docs", [])

print(f"총 {len(docs)}건의 도서 확인")
print()

# 모든 필드 확인
if docs:
    print("첫 번째 도서의 모든 필드:")
    first_doc = docs[0].get("doc", {})
    for key, value in first_doc.items():
        print(f"  {key}: {value}")
    print()

# 청구기호 관련 필드 확인
print("청구기호 관련 필드 분석:")
callno_fields = {}
for doc in docs[:20]:
    item = doc.get("doc", {})
    for key, value in item.items():
        if 'call' in key.lower() or 'class' in key.lower() or '청구' in key.lower():
            if key not in callno_fields:
                callno_fields[key] = []
            if value and value not in callno_fields[key]:
                callno_fields[key].append(str(value)[:50])

for field_name, values in callno_fields.items():
    print(f"\n{field_name}:")
    for val in values[:5]:
        print(f"  - {val}")
    if len(values) > 5:
        print(f"  ... 외 {len(values) - 5}개")

print()
print("=" * 60)
print("분석 완료")
print("=" * 60)






