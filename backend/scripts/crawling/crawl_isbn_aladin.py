import json
import time
import requests
import sys
import os

# config에서 API 키 가져오기
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.config import ALADIN_TTB_KEY

# 이전 크롤링 결과 읽기
with open('winter_books_callno_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 성공한 책들만 필터링
successful_books = [r for r in data['results'] if r['status'] == 'success']

print(f"🔍 알라딘 API로 ISBN 수집 시작 - 총 {len(successful_books)}권")
print(f"API 키: {ALADIN_TTB_KEY[:10]}...")
print()

ALADIN_URL = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"

results = []
success_count = 0
fail_count = 0

for i, book in enumerate(successful_books, 1):
    title = book['title']
    # 저자명 추출 (첫 번째 저자만)
    author_full = book.get('author', '')
    if not author_full:
        # callno에서 저자 추출 시도
        callno_text = book.get('callno', '')
        if '저자 :' in callno_text:
            author_part = callno_text.split('저자 :')[1].split('발행자')[0]
            author_full = author_part.strip()
    
    author = author_full.split()[0] if author_full else ''
    
    print(f"[{i}/{len(successful_books)}] {title}")
    print(f"  저자: {author}")
    
    try:
        params = {
            'ttbkey': ALADIN_TTB_KEY,
            'Query': title,
            'QueryType': 'Title',
            'MaxResults': 5,
            'start': 1,
            'SearchTarget': 'Book',
            'output': 'js',
            'Version': '20131101'
        }
        
        response = requests.get(ALADIN_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data_json = response.json()
        
        if data_json.get('item'):
            # 저자명으로 필터링
            matched_item = None
            
            for item in data_json['item']:
                item_author = item.get('author', '')
                item_title = item.get('title', '')
                
                # 저자명 매칭 (부분 일치)
                if author and author in item_author:
                    matched_item = item
                    break
                # 저자 없으면 제목으로만 매칭
                elif not author and title in item_title:
                    matched_item = item
                    break
            
            # 매칭 실패 시 첫 번째 결과 사용
            if not matched_item and data_json['item']:
                matched_item = data_json['item'][0]
            
            if matched_item:
                isbn = matched_item.get('isbn13') or matched_item.get('isbn')
                cover = matched_item.get('cover')
                publisher = matched_item.get('publisher')
                
                results.append({
                    'title': title,
                    'isbn': isbn,
                    'cover': cover,
                    'publisher': publisher,
                    'aladin_title': matched_item.get('title'),
                    'aladin_author': matched_item.get('author'),
                    'status': 'success'
                })
                success_count += 1
                print(f"  ✅ ISBN: {isbn}")
                if cover:
                    print(f"     표지: {cover[:50]}...")
            else:
                results.append({
                    'title': title,
                    'isbn': None,
                    'status': 'no_match'
                })
                fail_count += 1
                print(f"  ⚠️ 매칭 실패")
        else:
            results.append({
                'title': title,
                'isbn': None,
                'status': 'not_found'
            })
            fail_count += 1
            print(f"  ❌ 검색 결과 없음")
        
        time.sleep(0.5)  # API 부하 방지
        
    except Exception as e:
        results.append({
            'title': title,
            'isbn': None,
            'status': 'error',
            'error': str(e)
        })
        fail_count += 1
        print(f"  ❌ 에러: {e}")
        time.sleep(1)

print()
print("="*50)
print(f"✅ ISBN 수집 성공: {success_count}권")
print(f"❌ ISBN 수집 실패: {fail_count}권")
print(f"📊 성공률: {success_count/len(successful_books)*100:.1f}%")
print("="*50)

# 결과 저장
with open('winter_books_isbn_aladin.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(successful_books),
        'success': success_count,
        'fail': fail_count,
        'results': results
    }, f, ensure_ascii=False, indent=2)

print("\n✅ winter_books_isbn_aladin.json 파일로 저장 완료!")

# UPDATE SQL 생성
if success_count > 0:
    sql_lines = []
    sql_lines.append("-- 겨울방학 도서 ISBN 및 표지 이미지 업데이트 (알라딘 API)")
    sql_lines.append(f"-- ISBN 수집 결과: {success_count}/{len(successful_books)}권 성공")
    sql_lines.append("-- 생성일: 2026-01-19")
    sql_lines.append("")
    
    for result in results:
        if result['status'] == 'success' and result['isbn']:
            title_escaped = result['title'].replace("'", "''")
            isbn_escaped = result['isbn']
            
            sql = f"""UPDATE childbook_items 
SET isbn = '{isbn_escaped}'"""
            
            # 표지 이미지 추가
            if result.get('cover'):
                cover_escaped = result['cover'].replace("'", "''")
                sql += f",\n    image_url = '{cover_escaped}'"
            
            sql += f"""
WHERE title = '{title_escaped}' 
  AND curation_tag = '겨울방학2026';
"""
            
            comment = f"-- {result['title']}: ISBN {result['isbn']}"
            if result.get('aladin_title'):
                comment += f" (알라딘: {result['aladin_title']})"
            
            sql_lines.append(comment)
            sql_lines.append(sql)
    
    # 확인 쿼리
    sql_lines.append("")
    sql_lines.append("-- 확인 쿼리")
    sql_lines.append("SELECT title, isbn, image_url, pangyo_callno")
    sql_lines.append("FROM childbook_items")
    sql_lines.append("WHERE curation_tag = '겨울방학2026'")
    sql_lines.append("  AND isbn IS NOT NULL")
    sql_lines.append("ORDER BY title;")
    
    with open('update_winter_isbn_aladin.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    
    print(f"✅ update_winter_isbn_aladin.sql 파일 생성 완료! ({success_count}개 UPDATE 문)")
else:
    print("⚠️ 성공한 결과가 없어 SQL 파일을 생성하지 않았습니다.")

# 실패 목록
if fail_count > 0:
    print(f"\n⚠️ ISBN을 찾지 못한 책 ({fail_count}권):")
    for result in results:
        if result['status'] != 'success':
            print(f"  - {result['title']} ({result['status']})")
