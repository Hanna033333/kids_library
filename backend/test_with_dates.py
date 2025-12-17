"""날짜 조건 포함 API 테스트"""
import requests
from datetime import datetime, timedelta
from core.config import DATA4LIBRARY_KEY

PANGYO_CODE = "141231"
test_isbn = "9788936446819"

# 날짜 설정 (최근 10년)
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=3650)).strftime("%Y-%m-%d")

print(f"🏛️ 판교 도서관: {PANGYO_CODE}")
print(f"📖 ISBN: {test_isbn}")
print(f"📅 기간: {start_date} ~ {end_date}\n")

url = "http://data4library.kr/api/itemSrch"

# 시도 1: 날짜 + ISBN
print("=" * 70)
print("✅ 시도 1: startDt/endDt + isbn")
params1 = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "isbn": test_isbn,
    "startDt": start_date,
    "endDt": end_date,
    "format": "json",
    "pageNo": 1,
    "pageSize": 10
}
try:
    r = requests.get(url, params=params1, timeout=10)
    print(f"Status: {r.status_code}")
    if "error" in r.text:
        print(f"Response: {r.text[:200]}\n")
    else:
        print(f"✅ 성공! Response:\n{r.text[:1500]}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# 시도 2: type=ALL 추가
print("=" * 70)
print("✅ 시도 2: type=ALL + 날짜 + isbn")
params2 = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "type": "ALL",
    "isbn": test_isbn,
    "startDt": start_date,
    "endDt": end_date,
    "format": "json",
    "pageNo": 1,
    "pageSize": 10
}
try:
    r = requests.get(url, params=params2, timeout=10)
    print(f"Status: {r.status_code}")
    if "error" in r.text:
        print(f"Response: {r.text[:200]}\n")
    else:
        print(f"✅ 성공! Response:\n{r.text[:1500]}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# 시도 3: isbn13으로 변경
print("=" * 70)
print("✅ 시도 3: isbn13 + 날짜")
params3 = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "isbn13": test_isbn,
    "startDt": start_date,
    "endDt": end_date,
    "format": "json",
    "pageNo": 1,
    "pageSize": 10
}
try:
    r = requests.get(url, params=params3, timeout=10)
    print(f"Status: {r.status_code}")
    if "error" in r.text:
        print(f"Response: {r.text[:200]}\n")
    else:
        print(f"✅ 성공! Response:\n{r.text[:1500]}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# 시도 4: 제목 검색
print("=" * 70)
print("✅ 시도 4: keyword (제목) 검색")
params4 = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "keyword": "나미야 잡화점",
    "startDt": start_date,
    "endDt": end_date,
    "format": "json",
    "pageNo": 1,
    "pageSize": 3
}
try:
    r = requests.get(url, params=params4, timeout=10)
    print(f"Status: {r.status_code}")
    if "error" in r.text:
        print(f"Response: {r.text[:200]}\n")
    else:
        import json
        data = json.loads(r.text)
        print(f"✅ 성공!")
        print(f"검색 결과 수: {data.get('response', {}).get('numFound', 0)}")
        print(f"Response:\n{json.dumps(data, indent=2, ensure_ascii=False)[:2000]}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

