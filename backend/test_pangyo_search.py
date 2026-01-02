#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
판교 도서관 검색 테스트
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
import re

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 테스트 검색
title = "곰돌이 푸"
author = "밀른"
publisher = ""

print("="*80)
print(f"테스트 검색: {title} / {author}")
print("="*80)

search_url = "https://www.snlib.go.kr/pg/menu/10520/program/30010/plusSearchResultList.do"

params = {
    'searchKey1': 'TITLE',
    'searchKeyword1': title,
    'searchKey2': 'AUTHOR',
    'searchKeyword2': author,
    'searchKey3': 'PUBLISHER',
    'searchKeyword3': publisher,
    'searchLibrary': 'MP',
    'searchOrder': 'SIMILAR',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    print("\n검색 중...")
    response = requests.get(search_url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    response.encoding = 'utf-8'
    
    print(f"응답 코드: {response.status_code}")
    print(f"URL: {response.url}\n")
    
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 검색 결과 리스트 찾기
    result_list = soup.select('ul.resultList li')
    
    print(f"검색 결과: {len(result_list)}건\n")
    
    if result_list:
        # 첫 번째 결과 분석
        first_result = result_list[0]
        
        print("첫 번째 결과:")
        print("-"*80)
        
        # 제목
        title_elem = first_result.select_one('dt.title a')
        if title_elem:
            print(f"제목: {title_elem.get_text(strip=True)}")
        
        # 저자 정보
        author_dd = first_result.select('dd.author')
        print(f"\n저자 정보 섹션 수: {len(author_dd)}")
        
        for i, dd in enumerate(author_dd, 1):
            text = dd.get_text(strip=True)
            print(f"\n[{i}] {text[:200]}")
            
            # 청구기호 찾기
            if '청구기호' in text:
                print("   >>> 청구기호 발견!")
                match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', text)
                if match:
                    callno = match.group(1).strip()
                    print(f"   >>> 추출된 청구기호: {callno}")
        
        # 전체 텍스트에서도 찾기
        all_text = first_result.get_text()
        if '청구기호' in all_text:
            print("\n전체 텍스트에서 청구기호 검색:")
            match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', all_text)
            if match:
                callno = match.group(1).strip()
                print(f"   >>> 청구기호: {callno}")
    else:
        print("검색 결과가 없습니다.")
        print("\nHTML 일부:")
        print(soup.prettify()[:1000])
        
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
