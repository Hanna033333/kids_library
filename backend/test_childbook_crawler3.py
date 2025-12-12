import requests
from bs4 import BeautifulSoup

url = "https://www.childbook.org/book/recommend_list.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

res = requests.get(url, headers=headers, timeout=30)
res.encoding = 'utf-8'

soup = BeautifulSoup(res.text, 'html.parser')

# 모든 li 태그 확인
book_items = soup.find_all('li')

print(f"총 {len(book_items)}개의 li 태그\n")

# 텍스트가 긴 li 찾기 (책 정보일 가능성)
for i, li in enumerate(book_items):
    text = li.get_text(strip=True)
    if len(text) > 50:  # 긴 텍스트가 있는 li
        print(f"=== {i+1}번째 li (텍스트 길이: {len(text)}) ===")
        print(text[:300])
        print("\nHTML 구조:")
        print(str(li)[:500])
        print("\n" + "="*60 + "\n")
        if i >= 2:  # 처음 3개만 출력
            break








