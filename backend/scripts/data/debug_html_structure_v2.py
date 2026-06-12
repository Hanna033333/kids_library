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

output = []

if result_list:
    first_result = result_list[0]
    
    output.append("=== 첫 번째 검색 결과 HTML ===")
    output.append(first_result.prettify()[:3000])
    output.append("")
    
    # 모든 링크 찾기
    links = first_result.select('a')
    output.append(f"\n=== 링크 개수: {len(links)} ===")
    for i, link in enumerate(links, 1):
        output.append(f"\n링크 {i}:")
        output.append(f"  href: {link.get('href')}")
        output.append(f"  onclick: {link.get('onclick')}")
        output.append(f"  text: {link.get_text(strip=True)[:100]}")
    
    # dt a 태그 확인
    dt_link = first_result.select_one('dt a')
    if dt_link:
        output.append("\n=== dt > a 태그 ===")
        output.append(f"href: {dt_link.get('href')}")
        output.append(f"onclick: {dt_link.get('onclick')}")
        output.append(f"text: {dt_link.get_text(strip=True)}")
else:
    output.append("검색 결과 없음")

# 파일로 저장
with open('html_structure_debug.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("✅ html_structure_debug.txt 파일로 저장 완료!")
