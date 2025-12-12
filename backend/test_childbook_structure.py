import requests
from bs4 import BeautifulSoup

url = "https://www.childbook.org/book/recommend_list.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

res = requests.get(url, headers=headers, timeout=30)
res.encoding = 'utf-8'

soup = BeautifulSoup(res.text, 'html.parser')

# 첫 번째 책 정보가 있는 li 찾기
book_items = soup.find_all('li')
for item in book_items:
    text = item.get_text(strip=True)
    if len(text) > 50 and '#구멍' in text:
        print("=== 첫 번째 책 HTML 구조 ===")
        print(item.prettify())
        break








