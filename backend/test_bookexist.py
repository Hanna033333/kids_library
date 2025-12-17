"""bookExist API 테스트 - 실시간 대출 가능 여부"""
import requests
from core.config import DATA4LIBRARY_KEY

PANGYO_CODE = "141231"
test_books = [
    {"isbn": "9788936446819", "title": "수박 수영장"},
    {"isbn": "9788937460449", "title": "어린왕자"},
    {"isbn": "9788972756194", "title": "나미야 잡화점의 기적"},
]

print(f"🏛️ 판교 도서관: {PANGYO_CODE}")
print(f"🔑 API: bookExist (실시간 대출 가능 여부)\n")

url = "http://data4library.kr/api/bookExist"

for book in test_books:
    print("=" * 70)
    print(f"📖 테스트: {book['title']} ({book['isbn']})")
    
    # JSON 형식
    params_json = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "isbn13": book['isbn'],
        "format": "json"
    }
    
    try:
        r = requests.get(url, params=params_json, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Response (JSON):\n{r.text}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # XML 형식도 테스트
    params_xml = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_CODE,
        "isbn13": book['isbn'],
        "format": "xml"
    }
    
    try:
        r = requests.get(url, params=params_xml, timeout=10)
        print(f"Response (XML):\n{r.text[:500]}\n")
    except Exception as e:
        print(f"❌ XML Error: {e}\n")

