"""판교 도서관(141231) API 테스트"""
import requests
from core.config import DATA4LIBRARY_KEY

PANGYO_CODE = "141231"
test_isbn = "9788936446819"

print(f"🏛️ 판교 도서관 코드: {PANGYO_CODE}")
print(f"📖 테스트 ISBN: {test_isbn}\n")

# 시도 1: type=ALL + libCode
print("=" * 70)
print("✅ 시도 1: type=ALL + libCode + isbn")
url = "http://data4library.kr/api/itemSrch"
params = {
    "authKey": DATA4LIBRARY_KEY,
    "type": "ALL",
    "libCode": PANGYO_CODE,
    "isbn": test_isbn,
    "format": "json",
    "pageNo": 1,
    "pageSize": 10
}
print(f"URL: {url}")
print(f"Params: {params}\n")
try:
    r = requests.get(url, params=params, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response:\n{r.text}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# 시도 2: isbn13 사용
print("=" * 70)
print("✅ 시도 2: libCode + isbn13")
params2 = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "isbn13": test_isbn,
    "format": "json"
}
try:
    r = requests.get(url, params=params2, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response:\n{r.text}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# 시도 3: XML 형식
print("=" * 70)
print("✅ 시도 3: XML 형식")
params3 = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "isbn13": test_isbn,
    "format": "xml"
}
try:
    r = requests.get(url, params=params3, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response:\n{r.text[:1000]}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# 시도 4: 제목으로 검색 (대출 가능 여부 확인용)
print("=" * 70)
print("✅ 시도 4: 제목 검색 (keyword)")
params4 = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "keyword": "나미야",
    "format": "json",
    "pageNo": 1,
    "pageSize": 3
}
try:
    r = requests.get(url, params=params4, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response:\n{r.text}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

