#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML 응답 저장 및 분석
"""

import requests
from bs4 import BeautifulSoup

title = "곰돌이 푸"
author = "밀른"

search_url = "https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchResultList.do"

params = {
    'searchKey1': 'TITLE',
    'searchKeyword1': title,
    'searchKey2': 'AUTHOR',
    'searchKeyword2': author,
    'searchLibrary': 'MP',
    'searchOrder': 'SIMILAR',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("검색 중...")
response = requests.get(search_url, params=params, headers=headers, timeout=30)
response.encoding = 'utf-8'

# HTML 저장
with open('search_response.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"HTML 저장 완료: search_response.html")
print(f"응답 길이: {len(response.text)} bytes")

# 파싱
soup = BeautifulSoup(response.text, 'html.parser')
result_list = soup.select('ul.resultList li')

print(f"검색 결과: {len(result_list)}건")

if result_list:
    print("\n첫 번째 결과 HTML:")
    print("="*80)
    print(result_list[0].prettify()[:2000])
else:
    print("\n검색 결과가 없습니다!")
    print("\nHTML 일부:")
    print(response.text[:2000])
