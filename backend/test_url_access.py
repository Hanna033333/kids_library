"""웹사이트 URL 접근 테스트"""
import requests
from bs4 import BeautifulSoup

print("=" * 60)
print("웹사이트 URL 접근 테스트")
print("=" * 60)
print()

# 테스트할 URL들
test_urls = [
    "https://www.snlib.go.kr/",
    "https://www.snlib.go.kr/intro/menu/10041/program/30009/plusSearchResult.do",
]

for url in test_urls:
    print(f"테스트 URL: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        res = requests.get(url, headers=headers, timeout=10)
        print(f"  상태 코드: {res.status_code}")
        print(f"  응답 크기: {len(res.text)} bytes")
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find('title')
            if title:
                print(f"  페이지 제목: {title.get_text()[:50]}")
            
            # 검색 관련 요소 찾기
            search_inputs = soup.find_all(['input', 'form'], {'type': 'text'}) or soup.find_all('input', {'name': 'searchKeyword'})
            if search_inputs:
                print(f"  ✅ 검색 입력 필드 발견")
            else:
                print(f"  ⚠️  검색 입력 필드 없음")
        else:
            print(f"  ❌ 접근 실패")
            
    except Exception as e:
        print(f"  ❌ 오류: {e}")
    
    print()

print("=" * 60)

