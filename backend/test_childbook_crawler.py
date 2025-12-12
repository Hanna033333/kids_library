import requests
from bs4 import BeautifulSoup

url = "https://www.childbook.org/book/recommend_list.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

res = requests.get(url, headers=headers, timeout=30)
res.encoding = 'utf-8'

soup = BeautifulSoup(res.text, 'html.parser')

# 책 리스트가 있는 부분 찾기
print("=== 페이지 구조 분석 ===")
print()

# 모든 리스트 아이템 찾기
list_items = soup.find_all('li')
print(f"li 태그 개수: {len(list_items)}")

# 테이블 찾기
tables = soup.find_all('table')
print(f"table 태그 개수: {len(tables)}")

# div 태그 찾기
divs = soup.find_all('div', class_=True)
print(f"class가 있는 div 태그 개수: {len(divs)}")

# 책 제목이 포함된 부분 찾기
book_titles = soup.find_all(string=lambda text: text and ('구멍' in text or '100개의 키워드' in text))
print(f"\n책 제목 텍스트 발견: {len(book_titles)}개")

# 첫 번째 책 정보가 있는 부분 출력
print("\n=== 첫 번째 책 정보 부분 ===")
# '구멍'이라는 텍스트를 포함하는 요소 찾기
for elem in soup.find_all(string=lambda text: text and '구멍' in text):
    parent = elem.parent
    print(f"\n부모 태그: {parent.name}")
    print(f"부모 클래스: {parent.get('class')}")
    print(f"부모 내용: {str(parent)[:500]}")








