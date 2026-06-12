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
log_file = open('crawling_progress.log', 'a', encoding='utf-8') # Append mode
def log(msg):
    print(msg)
    log_file.write(msg + '\n')
    log_file.flush()

# 정규화 함수: 공백, 특수문자 제거
def normalize(text):
    if not text:
        return ""
    # 괄호와 그 안의 내용 제거 (예: (개정판), [도서] 등)
    text = re.sub(r'\(.*?\)|\[.*?\]', '', text)
    # 특수문자 제거, 공백 제거, 소문자 변환
    text = re.sub(r'[\s\W_]+', '', text).lower()
    return text

# JSON 파일 읽기
with open('winter_books_clean.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

log(f"\n🚀 크롤링 재시작... (총 {len(books)}권)")

BASE_URL = "https://www.snlib.go.kr/pg/plusSearchResultList.do"

# Load existing progress
results = []
done_titles = set()

if os.path.exists('crawling_results.jsonl'):
    with open('crawling_results.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                results.append(data)
                done_titles.add(data['title'])
            except: pass
    log(f"📋 이전 결과 {len(results)}건 로드 완료")

success_count = len([r for r in results if r.get('status') == 'success'])
fail_count = len([r for r in results if r.get('status') != 'success'])

for i, book in enumerate(books, 1):
    target_title = book['서명']
    if target_title in done_titles:
        # log(f"[{i}/{len(books)}] {target_title} (Skip: 이미 완료)")
        continue

    target_author = book['저자']
    target_publisher = book.get('발행자', '')
    
    # 저자 이름 첫 어절 추출
    target_author_key = target_author.split()[0] if target_author else ""
    
    # 정규화된 타겟 정보
    norm_target_title = normalize(target_title)
    norm_target_author = normalize(target_author_key)
    norm_target_publisher = normalize(target_publisher)
    
    log(f"[{i}/{len(books)}] {target_title} / {target_author_key} (진행중)")
    
    current_result = {'title': target_title, 'status': 'fail'} # Default

    try:
        params = {
            'searchKeyword': target_title,
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
                    is_author_match = norm_target_author in norm_item_text
                    is_publisher_match = norm_target_publisher in norm_item_text if norm_target_publisher else False
                    
                    callno = None
                    dd_elements = item.select('dl dd')
                    for dd in dd_elements:
                        text = dd.get_text(strip=True)
                        if '청구기호' in text:
                            # "저자: ... 청구기호: 123" 형태일 경우 "123"만 추출
                            parts = text.split('청구기호')
                            if len(parts) > 1:
                                candidate = parts[-1].replace(':', '').strip()
                                callno = candidate.split('위치출력')[0].strip()
                                break
                    
                    if not callno: continue

                    if is_title_match and is_author_match and is_publisher_match:
                        found_callno = callno
                        match_type = "Strict Match"
                        break 
                    
                    if not found_callno and is_title_match and is_author_match:
                        found_callno = callno
                        match_type = "Fallback Match"
                
                if found_callno:
                    current_result = {
                        'title': target_title,
                        'callno': found_callno,
                        'match_type': match_type,
                        'status': 'success'
                    }
                    success_count += 1
                    log(f"  ✅ {match_type}: {found_callno}")
                else:
                    current_result['status'] = 'mismatch'
                    fail_count += 1
                    log(f"  ⚠️ 매칭 실패")
            else:
                current_result['status'] = 'not_found'
                fail_count += 1
                log(f"  ❌ 검색 결과 없음")
        else:
            current_result['status'] = 'http_error'
            current_result['error'] = str(response.status_code)
            fail_count += 1
            log(f"  ❌ HTTP Error: {response.status_code}")

        time.sleep(1.0) 

    except Exception as e:
        current_result['status'] = 'error'
        current_result['error'] = str(e)
        fail_count += 1
        log(f"  ❌ 에러: {e}")
        time.sleep(2)
    
    # Save incrementally
    results.append(current_result)
    with open('crawling_results.jsonl', 'a', encoding='utf-8') as f:
        json.dump(current_result, f, ensure_ascii=False)
        f.write('\n')

# Final Report & SQL Generation
log("")
log("="*50)
log(f"✅ 성공: {success_count}권")
log(f"❌ 실패: {fail_count}권")
log("="*50)

if success_count > 0:
    sql_lines = []
    sql_lines.append("-- 겨울방학 도서 청구기호 정밀 업데이트 (Strict/Fallback Matching)")
    sql_lines.append(f"-- 성공: {success_count}/{len(books)}")
    sql_lines.append("")
    
    # Re-read results to ensure completeness
    # (Optional, but using memory 'results' is safer here to include previous runs)
    
    for res in results:
        if res.get('status') == 'success':
            title_esc = res['title'].replace("'", "''")
            callno_esc = res['callno'].replace("'", "''")
            sql = f"UPDATE childbook_items SET pangyo_callno = '{callno_esc}' WHERE title = '{title_esc}' AND curation_tag = '겨울방학2026';"
            sql_lines.append(f"-- {res.get('match_type', 'Unknown')}")
            sql_lines.append(sql)
            
    with open('update_winter_callno_v2.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    log("✅ update_winter_callno_v2.sql 생성 완료")
