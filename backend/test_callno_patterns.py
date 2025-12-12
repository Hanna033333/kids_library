"""
실제 수집된 데이터에서 청구기호 패턴 확인
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
print("청구기호 패턴 분석")
print("=" * 60)
print()

# 더 많은 데이터 수집
params = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": "2024-01-01",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 100,  # 더 많은 샘플
    "format": "json"
}

res = requests.get(url, params=params, timeout=30)
data = res.json()
docs = data.get("response", {}).get("docs", [])

print(f"총 {len(docs)}건 분석")
print()

# 청구기호 패턴 분석
patterns = {
    "아로 시작": [],
    "유로 시작": [],
    "한글 시작": [],
    "숫자 시작": [],
    "기타": []
}

for doc in docs:
    item = doc.get("doc", {})
    callno = item.get("class_no", "")
    title = item.get("bookname", "")
    
    if not callno:
        patterns["기타"].append((callno, title))
    elif callno.startswith("아"):
        patterns["아로 시작"].append((callno, title))
    elif callno.startswith("유"):
        patterns["유로 시작"].append((callno, title))
    elif callno and callno[0].isalpha() and ord('가') <= ord(callno[0]) <= ord('힣'):
        patterns["한글 시작"].append((callno, title))
    elif callno and callno[0].isdigit():
        patterns["숫자 시작"].append((callno, title))
    else:
        patterns["기타"].append((callno, title))

# 결과 출력
for pattern_name, items in patterns.items():
    count = len(items)
    print(f"{pattern_name}: {count}건")
    if items and count <= 10:
        for callno, title in items[:5]:
            print(f"  - {callno}: {title[:50]}")
    elif items:
        for callno, title in items[:3]:
            print(f"  - {callno}: {title[:50]}")
        print(f"  ... 외 {count - 3}건")
    print()

# 아동 관련 키워드가 있는 도서 확인
print("=" * 60)
print("제목에 아동 관련 키워드가 있는 도서:")
print("=" * 60)
child_keywords = ["아동", "유아", "어린이", "동화", "그림책", "아기", "아이", "키즈"]
child_books = []

for doc in docs:
    item = doc.get("doc", {})
    title = item.get("bookname", "")
    callno = item.get("class_no", "")
    
    if any(keyword in title for keyword in child_keywords):
        child_books.append((callno, title))

print(f"총 {len(child_books)}건 발견")
for callno, title in child_books[:10]:
    print(f"  - {callno}: {title}")

print()
print("=" * 60)
print("분석 완료")
print("=" * 60)






