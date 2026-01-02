#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
세션 기반 검색 테스트
"""

import requests
from bs4 import BeautifulSoup
import re

title = "곰돌이 푸"
author = "밀른"

# 세션 생성
session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("1. 검색 페이지 방문 중...")
# 먼저 검색 페이지 방문하여 세션/쿠키 획득
search_page_url = "https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchDetail.do"
session.get(search_page_url, headers=headers)

print("2. 검색 요청 중...")
# 이제 검색 실행
search_url = "https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchResultList.do"

data = {
    'searchKey1': 'TITLE',
    'searchKeyword1': title,
    'searchKey2': 'AUTHOR',
    'searchKeyword2': author,
    'searchKey3': 'PUBLISHER',
    'searchKeyword3': '',
    'searchLibrary': 'MP',
    'searchOrder': 'SIMILAR',
}

headers['Referer'] = search_page_url

response = session.post(search_url, data=data, headers=headers, timeout=30)
response.encoding = 'utf-8'

print(f"응답 코드: {response.status_code}")
print(f"응답 길이: {len(response.text)} bytes")

# 파싱
soup = BeautifulSoup(response.text, 'html.parser')
result_list = soup.select('ul.resultList li')

print(f"검색 결과: {len(result_list)}건")

if result_list:
    print("\n✅ 검색 성공!")
    
    first = result_list[0]
    
    # 제목
    title_elem = first.select_one('dt.title a')
    if title_elem:
        print(f"제목: {title_elem.get_text(strip=True)}")
    
    # 청구기호
    author_dd = first.select('dd.author')
    for dd in author_dd:
        text = dd.get_text(strip=True)
        if '청구기호' in text:
            print(f"청구기호 섹션: {text[:100]}")
            
            match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', text)
            if match:
                callno = match.group(1).strip()
                print(f"✅ 추출된 청구기호: {callno}")
else:
    print("\n❌ 검색 결과 없음")
    print("\nHTML 일부:")
    print(response.text[:500])
