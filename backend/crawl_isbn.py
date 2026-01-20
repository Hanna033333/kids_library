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

print(f"🔍 ISBN 크롤링 시작 (총 {len(successful_books)}권)")
print()

BASE_URL = "https://www.snlib.go.kr/pg/plusSearchResultList.do"

results = []
success_count = 0
fail_count = 0

for i, book in enumerate(successful_books, 1):
    title = book['title']
    
    print(f"[{i}/{len(successful_books)}] {title}")
    
    try:
        params = {
            'searchKeyword': title,
            'searchType': 'SIMPLE',
            'searchCategory': 'BOOK',
            'searchLibraryArr': 'MP',
            'searchKey': 'ALL',
            'topSearchType': 'BOOK'
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        result_list = soup.select('ul.resultList > li')
        
        if result_list:
            first_result = result_list[0]
            dd_elements = first_result.select('dl dd')
            
            isbn = None
            publisher = None
            year = None
            
            for dd in dd_elements:
                text = dd.get_text(strip=True)
                
                # ISBN 추출 (13자리 또는 10자리)
                if 'ISBN' in text.upper() or 'isbn' in text:
                    # 숫자만 추출
                    numbers = re.findall(r'\d+', text)
                    for num in numbers:
                        if len(num) == 13 or len(num) == 10:
                            isbn = num
                            break
                
                # 발행자
                if '발행자:' in text or '발행자 :' in text:
                    parts = text.split('발행자')
                    if len(parts) > 1:
                        publisher_part = parts[1].replace(':', '').strip()
                        # 발행연도 전까지
                        if '발행연도' in publisher_part:
                            publisher = publisher_part.split('발행연도')[0].strip()
                        else:
                            publisher = publisher_part.split()[0] if publisher_part else None
                
                # 발행연도
                if '발행연도:' in text or '발행연도 :' in text:
                    year_match = re.search(r'(\d{4})', text)
                    if year_match:
                        year = year_match.group(1)
            
            results.append({
                'title': title,
                'callno': book['callno'],
                'isbn': isbn,
                'publisher': publisher,
                'year': year,
                'status': 'success' if isbn else 'no_isbn'
            })
            
            if isbn:
                success_count += 1
                print(f"  ✅ ISBN: {isbn}")
                if publisher:
                    print(f"     출판사: {publisher}")
                if year:
                    print(f"     발행연도: {year}")
            else:
                fail_count += 1
                print(f"  ⚠️ ISBN 없음")
        else:
            results.append({
                'title': title,
                'callno': book['callno'],
                'isbn': None,
                'publisher': None,
                'year': None,
                'status': 'not_found'
            })
            fail_count += 1
            print(f"  ❌ 검색 결과 없음")
        
        time.sleep(1.5)
        
    except Exception as e:
        results.append({
            'title': title,
            'callno': book['callno'],
            'isbn': None,
            'publisher': None,
            'year': None,
            'status': 'error',
            'error': str(e)
        })
        fail_count += 1
        print(f"  ❌ 에러: {e}")
        time.sleep(2)

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
    sql_lines.append("-- 겨울방학 도서 ISBN 및 메타데이터 업데이트")
    sql_lines.append(f"-- ISBN 수집 결과: {success_count}/{len(successful_books)}권 성공")
    sql_lines.append("-- 생성일: 2026-01-19")
    sql_lines.append("")
    
    for result in results:
        if result['isbn']:
            title_escaped = result['title'].replace("'", "''")
            isbn_escaped = result['isbn']
            
            # 기본 UPDATE (ISBN만)
            sql = f"""UPDATE childbook_items 
SET isbn = '{isbn_escaped}'"""
            
            # 출판사 추가
            if result.get('publisher'):
                publisher_escaped = result['publisher'].replace("'", "''")
                sql += f",\n    publisher = '{publisher_escaped}'"
            
            # 발행연도 추가
            if result.get('year'):
                sql += f",\n    published_year = {result['year']}"
            
            sql += f"""
WHERE title = '{title_escaped}' 
  AND curation_tag = '겨울방학2026';
"""
            
            comment = f"-- {result['title']}: ISBN {result['isbn']}"
            if result.get('publisher'):
                comment += f", {result['publisher']}"
            if result.get('year'):
                comment += f", {result['year']}"
            
            sql_lines.append(comment)
            sql_lines.append(sql)
    
    # 확인 쿼리
    sql_lines.append("")
    sql_lines.append("-- 확인 쿼리")
    sql_lines.append("SELECT title, isbn, publisher, published_year, pangyo_callno")
    sql_lines.append("FROM childbook_items")
    sql_lines.append("WHERE curation_tag = '겨울방학2026'")
    sql_lines.append("  AND isbn IS NOT NULL")
    sql_lines.append("ORDER BY title;")
    
    with open('update_winter_isbn.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    
    print(f"✅ update_winter_isbn.sql 파일 생성 완료! ({success_count}개 UPDATE 문)")
else:
    print("⚠️ 성공한 결과가 없어 SQL 파일을 생성하지 않았습니다.")
