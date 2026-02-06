import json
import time
import requests
import sys
import os

# config에서 API 키 가져오기
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.config import ALADIN_TTB_KEY

# 칼데콧 기본 데이터 읽기
with open('caldecott_base.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

print(f"🔍 알라딘 API로 칼데콧 수상작 데이터 수집 시작 - 총 {len(books)}권")
print(f"API 키: {ALADIN_TTB_KEY[:10]}...")
print()

ALADIN_URL = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"

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
    
    print(f"[{i}/{len(books)}] {year}년 - {search_title}")
    print(f"  원제: {original_title}")
    print(f"  작가: {author} / 그림: {illustrator}")
    
    try:
        params = {
            'ttbkey': ALADIN_TTB_KEY,
            'Query': f"{original_title} {author}",
            'QueryType': 'Keyword',
            'MaxResults': 10,
            'start': 1,
            'SearchTarget': 'Book',
            'output': 'js',
            'Version': '20131101'
        }
        
        response = requests.get(ALADIN_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data_json = response.json()
        
        if data_json.get('item'):
            if "Big" in original_title:
                print(f"DEBUG: Raw item keys: {data_json['item'][0].keys()}")
                print(f"DEBUG: Raw item: {json.dumps(data_json['item'][0], ensure_ascii=False)}")
                
            # 매칭 로직: 제목 + 저자/그림작가
            matched_item = None
            
            for item in data_json['item']:
                item_author = item.get('author', '')
                item_title = item.get('title', '')
                
                # 제목 매칭 (부분 일치)
                title_match = (search_title.lower() in item_title.lower()) or (item_title.lower() in search_title.lower())
                
                # 저자 또는 그림작가 매칭
                author_match = False
                if author_key and author_key in item_author:
                    author_match = True
                elif illustrator and illustrator.split()[0] in item_author:
                    author_match = True
                
                # 원제 매칭 추가
                original_match = (original_title.lower() in item_title.lower()) or (item_title.lower() in original_title.lower())
                
                # 제목이 매칭되면 (한글 또는 원제), 저자 매칭 실패해도 우선 허용 (로그 남김)
                if title_match or original_match:
                    matched_item = item
                    if not author_match:
                        print(f"    ⚠️ 저자 불일치 허용: {item_author} (검색어: {author})")
                    break
            
            # 매칭 실패해도 첫 번째 결과 사용 (검색어가 구체적이므로 신뢰)
            # 단, 검색어에 저자가 포함된 경우에만
            if not matched_item and data_json['item']:
                matched_item = data_json['item'][0]
                print(f"    ⚠️ 첫 번째 결과 채택 (검색어: {original_title} {author})")
                print(f"       -> {matched_item.get('title')} / {matched_item.get('author')}")
            
            if matched_item:
                isbn = matched_item.get('isbn13') or matched_item.get('isbn')
                cover = matched_item.get('cover')
                publisher = matched_item.get('publisher')
                description = matched_item.get('description', '')
                
                results.append({
                    'year': year,
                    'korean_title': korean_title,
                    'original_title': original_title,
                    'author': author,
                    'illustrator': illustrator,
                    'isbn': isbn,
                    'cover': cover,
                    'publisher': publisher,
                    'description': description,
                    'aladin_title': matched_item.get('title'),
                    'aladin_author': matched_item.get('author'),
                    'status': 'success'
                })
                success_count += 1
                print(f"  ✅ ISBN: {isbn}")
                if cover:
                    print(f"     표지: {cover[:60]}...")
            else:
                results.append({
                    **book,
                    'isbn': None,
                    'cover': None,
                    'publisher': None,
                    'description': None,
                    'status': 'no_match'
                })
                fail_count += 1
                print(f"  ⚠️ 매칭 실패")
        else:
            results.append({
                **book,
                'isbn': None,
                'cover': None,
                'publisher': None,
                'description': None,
                'status': 'not_found'
            })
            fail_count += 1
            print(f"  ❌ 검색 결과 없음")
        
        time.sleep(0.5)  # API 부하 방지
        
    except Exception as e:
        results.append({
            **book,
            'isbn': None,
            'cover': None,
            'publisher': None,
            'description': None,
            'status': 'error',
            'error': str(e)
        })
        fail_count += 1
        print(f"  ❌ 에러: {e}")
        time.sleep(1)

print()
print("="*50)
print(f"✅ 데이터 수집 성공: {success_count}권")
print(f"❌ 데이터 수집 실패: {fail_count}권")
print(f"📊 성공률: {success_count/len(books)*100:.1f}%")
print("="*50)

# 결과 저장
with open('caldecott_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n✅ caldecott_enriched.json 파일로 저장 완료!")

# UPDATE SQL 생성
if success_count > 0:
    sql_lines = []
    sql_lines.append("-- 칼데콧 수상작 ISBN 및 표지 이미지 업데이트 (알라딘 API)")
    sql_lines.append(f"-- ISBN 수집 결과: {success_count}/{len(books)}권 성공")
    sql_lines.append("-- 생성일: 2026-02-06")
    sql_lines.append("")
    
    for result in results:
        if result['status'] == 'success' and result['isbn']:
            # 매칭된 책의 제목은 알라딘 제목이 아니라, DB에 있는 제목을 기준으로 업데이트해야 함
            # 하지만 DB에 있는 제목(Korean Title)이 없는 경우(신간 등)는 어떻게?
            # 여기서는 DB에 이미 삽입된 데이터의 Title을 기준으로 업데이트한다고 가정
            # caldecott_base.json의 korean_title이 있으면 그것을, 없으면 original_title을 사용?
            # insert_caldecott_final.sql 에서는 korean_title이 있으면 그것을, 없으면 original_title을 Title로 사용했음.
            
            target_title = result.get('korean_title') or result['original_title']
            title_escaped = target_title.replace("'", "''")
            isbn_escaped = result['isbn']
            
            sql = f"""UPDATE childbook_items 
SET isbn = '{isbn_escaped}'"""
            
            # 표지 이미지 추가/업데이트
            if result.get('cover'):
                cover_escaped = result['cover'].replace("'", "''")
                sql += f",\n    image_url = '{cover_escaped}'"
            
            sql += f"""
WHERE title = '{title_escaped}' 
  AND curation_tag LIKE '%caldecott%';
"""
            
            comment = f"-- {target_title}: ISBN {result['isbn']}"
            if result.get('aladin_title'):
                comment += f" (알라딘: {result['aladin_title']})"
            
            sql_lines.append(comment)
            sql_lines.append(sql)
    
    # 확인 쿼리
    sql_lines.append("")
    sql_lines.append("-- 확인 쿼리")
    sql_lines.append("SELECT title, isbn, image_url, pangyo_callno")
    sql_lines.append("FROM childbook_items")
    sql_lines.append("WHERE curation_tag LIKE '%caldecott%'")
    sql_lines.append("ORDER BY title;")
    
    with open('update_caldecott_isbn_v2.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    
    print(f"✅ update_caldecott_isbn_v2.sql 파일 생성 완료! ({success_count}개 UPDATE 문)")

# 실패 목록
if fail_count > 0:
    print(f"\n⚠️ 데이터를 찾지 못한 책 ({fail_count}권):")
    for result in results:
        if result['status'] != 'success':
            print(f"  - {result['year']}년: {result.get('korean_title') or result['original_title']} ({result['status']})")
