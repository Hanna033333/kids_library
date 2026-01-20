import json
import time
import requests
from bs4 import BeautifulSoup
import re

# 이전 크롤링 결과 읽기
with open('winter_books_callno_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 성공한 책들만 필터링
successful_books = [r for r in data['results'] if r['status'] == 'success']

print(f"🔍 ISBN 크롤링 시작 (상세 페이지) - 총 {len(successful_books)}권")
print()

SEARCH_URL = "https://www.snlib.go.kr/pg/plusSearchResultList.do"
DETAIL_URL = "https://www.snlib.go.kr/pg/menu/10519/program/30009/plusSearchResultDetail.do"

results = []
success_count = 0
fail_count = 0

for i, book in enumerate(successful_books, 1):
    title = book['title']
    
    print(f"[{i}/{len(successful_books)}] {title}")
    
    try:
        # 1단계: 검색하여 recKey와 bookKey 찾기
        params = {
            'searchKeyword': title,
            'searchType': 'SIMPLE',
            'searchCategory': 'BOOK',
            'searchLibraryArr': 'MP',
            'searchKey': 'ALL',
            'topSearchType': 'BOOK'
        }
        
        response = requests.get(SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        result_list = soup.select('ul.resultList > li')
        
        if not result_list:
            results.append({
                'title': title,
                'callno': book['callno'],
                'isbn': None,
                'status': 'not_found'
            })
            fail_count += 1
            print(f"  ❌ 검색 결과 없음")
            continue
        
        # 첫 번째 결과에서 링크 찾기
        first_result = result_list[0]
        link = first_result.select_one('dt a')
        
        if not link or not link.get('onclick'):
            results.append({
                'title': title,
                'callno': book['callno'],
                'isbn': None,
                'status': 'no_link'
            })
            fail_count += 1
            print(f"  ❌ 상세 링크 없음")
            continue
        
        # onclick에서 recKey와 bookKey 추출
        onclick = link.get('onclick', '')
        # 예: goDetail('1949734267', '1949734269')
        keys = re.findall(r"'(\d+)'", onclick)
        
        if len(keys) < 2:
            results.append({
                'title': title,
                'callno': book['callno'],
                'isbn': None,
                'status': 'no_keys'
            })
            fail_count += 1
            print(f"  ❌ recKey/bookKey 추출 실패")
            continue
        
        rec_key = keys[0]
        book_key = keys[1]
        
        # 2단계: 상세 페이지 크롤링
        detail_params = {
            'recKey': rec_key,
            'bookKey': book_key
        }
        
        detail_response = requests.get(DETAIL_URL, params=detail_params, timeout=10)
        detail_response.raise_for_status()
        
        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
        
        # 표준번호 찾기
        isbn = None
        th_elements = detail_soup.select('th')
        
        for th in th_elements:
            if '표준번호' in th.get_text():
                td = th.find_next_sibling('td')
                if td:
                    isbn_text = td.get_text(strip=True)
                    # ISBN 숫자만 추출 (13자리 또는 10자리)
                    numbers = re.findall(r'\d+', isbn_text)
                    for num in numbers:
                        if len(num) == 13 or len(num) == 10:
                            isbn = num
                            break
                break
        
        if isbn:
            results.append({
                'title': title,
                'callno': book['callno'],
                'isbn': isbn,
                'status': 'success'
            })
            success_count += 1
            print(f"  ✅ ISBN: {isbn}")
        else:
            results.append({
                'title': title,
                'callno': book['callno'],
                'isbn': None,
                'status': 'no_isbn_in_detail'
            })
            fail_count += 1
            print(f"  ⚠️ 상세 페이지에 ISBN 없음")
        
        time.sleep(2)  # 상세 페이지까지 접근하므로 대기 시간 증가
        
    except Exception as e:
        results.append({
            'title': title,
            'callno': book['callno'],
            'isbn': None,
            'status': 'error',
            'error': str(e)
        })
        fail_count += 1
        print(f"  ❌ 에러: {e}")
        time.sleep(3)

print()
print("="*50)
print(f"✅ ISBN 수집 성공: {success_count}권")
print(f"❌ ISBN 수집 실패: {fail_count}권")
print(f"📊 성공률: {success_count/len(successful_books)*100:.1f}%")
print("="*50)

# 결과 저장
with open('winter_books_isbn_results.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(successful_books),
        'success': success_count,
        'fail': fail_count,
        'results': results
    }, f, ensure_ascii=False, indent=2)

print("\n✅ winter_books_isbn_results.json 파일로 저장 완료!")

# UPDATE SQL 생성
if success_count > 0:
    sql_lines = []
    sql_lines.append("-- 겨울방학 도서 ISBN 업데이트")
    sql_lines.append(f"-- ISBN 수집 결과: {success_count}/{len(successful_books)}권 성공")
    sql_lines.append("-- 생성일: 2026-01-19")
    sql_lines.append("")
    
    for result in results:
        if result['status'] == 'success' and result['isbn']:
            title_escaped = result['title'].replace("'", "''")
            
            sql = f"""UPDATE childbook_items 
SET isbn = '{result['isbn']}'
WHERE title = '{title_escaped}' 
  AND curation_tag = '겨울방학2026';
"""
            sql_lines.append(f"-- {result['title']}: {result['isbn']}")
            sql_lines.append(sql)
    
    # 확인 쿼리
    sql_lines.append("")
    sql_lines.append("-- 확인 쿼리")
    sql_lines.append("SELECT title, isbn, pangyo_callno")
    sql_lines.append("FROM childbook_items")
    sql_lines.append("WHERE curation_tag = '겨울방학2026'")
    sql_lines.append("  AND isbn IS NOT NULL")
    sql_lines.append("ORDER BY title;")
    
    with open('update_winter_isbn.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    
    print(f"✅ update_winter_isbn.sql 파일 생성 완료! ({success_count}개 UPDATE 문)")
else:
    print("⚠️ 성공한 결과가 없어 SQL 파일을 생성하지 않았습니다.")

# 실패 목록
if fail_count > 0:
    print(f"\n⚠️ ISBN을 찾지 못한 책 ({fail_count}권):")
    for result in results:
        if result['status'] != 'success':
            print(f"  - {result['title']} ({result['status']})")
