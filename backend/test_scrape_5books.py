#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
판교 도서관 검색 테스트 - 5권만
"""

import sys
import io
import requests
from bs4 import BeautifulSoup
import time
import re
from supabase_client import supabase

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def search_pangyo_library(title, author, publisher):
    """판교 도서관 검색"""
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
        response = requests.get(search_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        result_list = soup.select('ul.resultList li')
        
        if not result_list:
            return None
        
        first_result = result_list[0]
        
        # 청구기호 찾기
        author_dd = first_result.select('dd.author')
        
        for dd in author_dd:
            text = dd.get_text(strip=True)
            
            if '청구기호' in text:
                match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', text)
                if match:
                    return match.group(1).strip()
        
        # 전체 텍스트에서 찾기
        all_text = first_result.get_text()
        match = re.search(r'청구기호\s*[:：]\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s*$|\s*[|]|\s*대출)', all_text)
        if match:
            return match.group(1).strip()
        
        return None
        
    except Exception as e:
        print(f"검색 오류: {e}")
        return None


# DB에서 5권만 조회
print("DB에서 5권 조회 중...")
response = supabase.table("childbook_items").select(
    "id, title, author, publisher"
).limit(5).execute()

books = response.data
print(f"조회 완료: {len(books)}권\n")

# 각 책 검색
for i, book in enumerate(books, 1):
    title = book.get('title', '')
    author = book.get('author', '')
    publisher = book.get('publisher', '')
    
    print(f"[{i}/5] {title[:30]}")
    print(f"  저자: {author[:20]}")
    print(f"  출판사: {publisher[:20]}")
    
    callno = search_pangyo_library(title, author or '', publisher or '')
    
    if callno:
        print(f"  ✅ 청구기호: {callno}")
        
        # DB 업데이트
        try:
            supabase.table("childbook_items").update({
                "web_scraped_callno": callno
            }).eq("id", book['id']).execute()
            print(f"  💾 DB 업데이트 완료")
        except Exception as e:
            print(f"  ❌ 업데이트 오류: {e}")
    else:
        print(f"  ⚠️  청구기호 없음")
    
    print()
    time.sleep(1)

print("\n완료!")
