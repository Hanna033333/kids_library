"""권차 API 간단 테스트"""
import requests
import json
from datetime import datetime, timedelta
from core.config import DATA4LIBRARY_KEY

PANGYO_LIB_CODE = "141231"
end_date = datetime.now()
start_date = end_date - timedelta(days=365*5)

# 테스트 ISBN
test_isbn = "9788949162010"  # 임의의 ISBN

url = "http://data4library.kr/api/itemSrch"
params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_LIB_CODE,
    "isbn13": test_isbn,
    "startDt": start_date.strftime("%Y-%m-%d"),
    "endDt": end_date.strftime("%Y-%m-%d"),
    "format": "json",
    "pageSize": 100
}

print(f"Testing ISBN: {test_isbn}")
print(f"URL: {url}")
print(f"Params: {params}\n")

resp = requests.get(url, params=params, timeout=10)
data = resp.json()

# JSON 파일로 저장
with open('volume_api_response.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Response saved to volume_api_response.json")
print(f"Status: {resp.status_code}")

result = data.get("response", {}).get("result", [])
print(f"Result count: {len(result)}")

if result:
    print("\nFirst item fields:")
    print(json.dumps(result[0], ensure_ascii=False, indent=2))
