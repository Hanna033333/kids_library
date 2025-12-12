import requests
from bs4 import BeautifulSoup

url = "https://www.childbook.org/book/recommend_list.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

res = requests.get(url, headers=headers, timeout=30)
res.encoding = 'utf-8'

soup = BeautifulSoup(res.text, 'html.parser')

# '구멍' 책이 포함된 리스트 아이템 찾기
book_items = soup.find_all('li')

print(f"총 {len(book_items)}개의 li 태그 발견\n")

# 첫 번째 책 정보가 있는 li 찾기
for i, li in enumerate(book_items[:5]):
    if '구멍' in li.get_text() or '100개의 키워드' in li.get_text():
        print(f"=== {i+1}번째 li (책 정보 포함) ===")
        print(li.prettify()[:1000])
        print("\n" + "="*60 + "\n")








