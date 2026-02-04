# -*- coding: utf-8 -*-
import sys
import io
import os
import json
import time
import requests
import re
from bs4 import BeautifulSoup

# 콘솔 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Helper for logging
log_file = open('caldecott_crawling.log', 'w', encoding='utf-8')
def log(msg):
    print(msg)
    log_file.write(msg + '\n')
    log_file.flush()

# 정규화 함수: 공백, 특수문자 제거
def normalize(text):
    if not text:
        return ""
    # 괄호와 그 안의 내용 제거
    text = re.sub(r'\(.*?\)|\[.*?\]', '', text)
    # 특수문자 제거, 공백 제거, 소문자 변환
    text = re.sub(r'[\s\W_]+', '', text).lower()
    return text

# JSON 파일 읽기
with open('caldecott_enriched.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

log(f"\n🚀 판교도서관 청구기호 크롤링 시작... (총 {len(books)}권)")

BASE_URL = "https://www.snlib.go.kr/pg/plusSearchResultList.do"

results = []
success_count = 0
fail_count = 0

for i, book in enumerate(books, 1):
    year = book['year']
    korean_title = book.get('korean_title')
    original_title = book['original_title']
    author = book.get('author', '')
    illustrator = book.get('illustrator', '')
    
    # 검색 우선순위: 한글 제목 > 원제
    search_title = korean_title if korean_title else original_title
    
    # 저자명 추출 (성만)
    author_key = author.split()[0] if author else ''
    illustrator_key = illustrator.split()[0] if illustrator else ''
    
    # 정규화된 타겟 정보
    norm_target_title = normalize(search_title)
    norm_target_author = normalize(author_key)
    norm_target_illustrator = normalize(illustrator_key)
    
    log(f"[{i}/{len(books)}] {year}년 - {search_title}")
    
    current_result = {**book, 'pangyo_callno': None, 'crawl_status': 'fail'}
    
    try:
        params = {
            'searchKeyword': search_title,
            'searchType': 'SIMPLE',
            'searchCategory': 'BOOK',
            'searchLibraryArr': 'MP',
            'searchKey': 'ALL',
            'topSearchType': 'BOOK'
        }
        
        response = requests.get(BASE_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            result_items = soup.select('ul.resultList > li')
            
            found_callno = None
            match_type = None
            
            if result_items:
                for idx, item in enumerate(result_items):
                    title_elem = item.select_one('.tit a')
                    result_title = title_elem.get_text(strip=True) if title_elem else ""
                    item_text = item.get_text(strip=True)
                    
                    norm_result_title = normalize(result_title)
                    norm_item_text = normalize(item_text)
                    
                    is_title_match = (norm_target_title in norm_result_title) or (norm_result_title in norm_target_title)
                    is_author_match = norm_target_author in norm_item_text if norm_target_author else False
                    is_illustrator_match = norm_target_illustrator in norm_item_text if norm_target_illustrator else False
                    
                    callno = None
                    dd_elements = item.select('dl dd')
                    for dd in dd_elements:
                        text = dd.get_text(strip=True)
                        if '청구기호' in text:
                            parts = text.split('청구기호')
                            if len(parts) > 1:
                                candidate = parts[-1].replace(':', '').strip()
                                callno = candidate.split('위치출력')[0].strip()
                                break
                    
                    if not callno:
                        continue
                    
                    # Strict Match: 제목 + (저자 or 그림작가)
                    if is_title_match and (is_author_match or is_illustrator_match):
                        found_callno = callno
                        match_type = "Strict Match"
                        break
                    
                    # Fallback: 제목만 일치
                    if not found_callno and is_title_match:
                        found_callno = callno
                        match_type = "Title Only"
                
                if found_callno:
                    current_result['pangyo_callno'] = found_callno
                    current_result['crawl_status'] = 'success'
                    current_result['match_type'] = match_type
                    success_count += 1
                    log(f"  ✅ {match_type}: {found_callno}")
                else:
                    current_result['crawl_status'] = 'mismatch'
                    fail_count += 1
                    log(f"  ⚠️ 매칭 실패")
            else:
                current_result['crawl_status'] = 'not_found'
                fail_count += 1
                log(f"  ❌ 검색 결과 없음")
        else:
            current_result['crawl_status'] = 'http_error'
            current_result['error'] = str(response.status_code)
            fail_count += 1
            log(f"  ❌ HTTP Error: {response.status_code}")
        
        time.sleep(1.0)
        
    except Exception as e:
        current_result['crawl_status'] = 'error'
        current_result['error'] = str(e)
        fail_count += 1
        log(f"  ❌ 에러: {e}")
        time.sleep(2)
    
    results.append(current_result)

log("")
log("="*50)
log(f"✅ 성공: {success_count}권")
log(f"❌ 실패: {fail_count}권")
log("="*50)

# 결과 저장
with open('caldecott_final.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

log("\n✅ caldecott_final.json 파일로 저장 완료!")

log_file.close()
