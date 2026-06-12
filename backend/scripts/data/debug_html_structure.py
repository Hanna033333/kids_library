import json
import time
import requests
from bs4 import BeautifulSoup
import re

# 테스트: 첫 번째 책만
title = "나는 오늘도 감정식당에 가요"

SEARCH_URL = "https://www.snlib.go.kr/pg/plusSearchResultList.do"

params = {
    'searchKeyword': title,
    'searchType': 'SIMPLE',
    'searchCategory': 'BOOK',
    'searchLibraryArr': 'MP',
    'searchKey': 'ALL',
    'topSearchType': 'BOOK'
}

response = requests.get(SEARCH_URL, params=params, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

# 첫 번째 결과의 HTML 구조 확인
result_list = soup.select('ul.resultList > li')

if result_list:
    first_result = result_list[0]
    
    print("=== 첫 번째 검색 결과 HTML ===")
    print(first_result.prettify()[:2000])
    print()
    
    # 모든 링크 찾기
    links = first_result.select('a')
    print(f"\n=== 링크 개수: {len(links)} ===")
    for i, link in enumerate(links, 1):
        print(f"\n링크 {i}:")
        print(f"  href: {link.get('href')}")
        print(f"  onclick: {link.get('onclick')}")
        print(f"  text: {link.get_text(strip=True)[:50]}")
    
    # dt a 태그 확인
    dt_link = first_result.select_one('dt a')
    if dt_link:
        print("\n=== dt > a 태그 ===")
        print(f"href: {dt_link.get('href')}")
        print(f"onclick: {dt_link.get('onclick')}")
        print(f"text: {dt_link.get_text(strip=True)}")
else:
    print("검색 결과 없음")
