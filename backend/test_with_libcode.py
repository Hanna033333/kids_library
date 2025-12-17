"""도서관 코드 포함 API 테스트"""
import requests
from core.config import DATA4LIBRARY_KEY

test_isbn = "9788936446819"
lib_code = "MA0003"  # 판교 도서관

print(f"📚 도서관 코드: {lib_code}")
print(f"📖 ISBN: {test_isbn}\n")

url = "http://data4library.kr/api/itemSrch"
params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": lib_code,
    "isbn13": test_isbn,
    "format": "json",
    "pageNo": 1,
    "pageSize": 10
}

print("🔍 요청 URL:", url)
print("📋 파라미터:", params)
print()

try:
    r = requests.get(url, params=params, timeout=10)
    print(f"✅ Status: {r.status_code}")
    print(f"📄 Response:\n{r.text}")
except Exception as e:
    print(f"❌ Error: {e}")

