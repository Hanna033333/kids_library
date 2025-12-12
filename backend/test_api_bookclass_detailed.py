"""
bookClass=CHILD 파라미터로 실제 아동 도서가 필터링되는지 상세 테스트
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
print("bookClass=CHILD 상세 테스트")
print("=" * 60)
print()

# bookClass 없이 요청 (전체)
print("1. bookClass 없이 요청 (전체 도서):")
params_all = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": "2024-12-01",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 10,
    "format": "json"
}

res_all = requests.get(url, params=params_all, timeout=30)
data_all = res_all.json()
numFound_all = data_all.get("response", {}).get("numFound", 0)
print(f"   전체 도서 수: {numFound_all}건")
print()

# bookClass=CHILD로 요청
print("2. bookClass=CHILD로 요청:")
params_child = {
    "authKey": DATA4LIBRARY_KEY,
    "libCode": PANGYO_CODE,
    "startDt": "2024-12-01",
    "endDt": "2024-12-31",
    "pageNo": 1,
    "pageSize": 50,  # 더 많은 샘플 확인
    "format": "json",
    "bookClass": "CHILD"
}

res_child = requests.get(url, params=params_child, timeout=30)
data_child = res_child.json()
docs_child = data_child.get("response", {}).get("docs", [])
numFound_child = data_child.get("response", {}).get("numFound", 0)

print(f"   아동 도서 수: {numFound_child}건")
print(f"   샘플: {len(docs_child)}건")
print()

# 청구기호 분석
print("3. 청구기호 분석:")
callno_patterns = {
    "아로 시작": 0,
    "유로 시작": 0,
    "KDC 0-99": 0,
    "기타": 0
}

child_keywords = ["아동", "유아", "어린이", "동화", "그림책", "아기"]

for doc in docs_child:
    item = doc.get("doc", {})
    callno = item.get("class_no", "")
    title = item.get("bookname", "")
    
    if callno.startswith("아"):
        callno_patterns["아로 시작"] += 1
    elif callno.startswith("유"):
        callno_patterns["유로 시작"] += 1
    else:
        try:
            prefix = int(callno.split('.')[0])
            if 0 <= prefix <= 99:
                callno_patterns["KDC 0-99"] += 1
            else:
                callno_patterns["기타"] += 1
        except:
            callno_patterns["기타"] += 1

for pattern, count in callno_patterns.items():
    print(f"   {pattern}: {count}건")

print()
print("4. 제목에 아동 관련 키워드가 있는 도서:")
child_title_count = 0
for doc in docs_child[:20]:  # 처음 20개만 확인
    item = doc.get("doc", {})
    title = item.get("bookname", "")
    if any(keyword in title for keyword in child_keywords):
        child_title_count += 1
        print(f"   - {title}")

print(f"\n   아동 키워드 포함: {child_title_count}건 / 20건")
print()

# 비교: bookClass 없이 vs CHILD
print("5. 비교:")
print(f"   전체 도서: {numFound_all}건")
print(f"   bookClass=CHILD: {numFound_child}건")
print(f"   차이: {numFound_all - numFound_child}건")
print()

print("=" * 60)
print("테스트 완료")
print("=" * 60)






