import requests
import json
import sys
import os

# config에서 API 키 가져오기
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.config import ALADIN_TTB_KEY

# 수동으로 입력받은 ISBN들
manual_books = [
    {
        "title": "책 요정 도도 : 도서관을 구해 줘!",
        "isbn": "9791194098034"
    },
    {
        "title": "불안이 사르르 사라지는 그림책 : 작은 일에도 걱정부터 앞서는 아이를 위한 마음 사용법",
        "isbn": "9791140713585"
    },
    {
        "title": "일곱 빛깔 감정 나라 : 내 안의 다채로운 감정과 만나는 곳",
        "isbn": "9791168272941"
    }
]

print(f"🔍 수동 입력 ISBN 정보 조회 (총 {len(manual_books)}권)")
print(f"API 키: {ALADIN_TTB_KEY[:10]}...")
print()

ALADIN_URL = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"

results = []

for book in manual_books:
    title = book['title']
    isbn = book['isbn']
    
    print(f"검색: {title} (ISBN: {isbn})")
    
    try:
        params = {
            'ttbkey': ALADIN_TTB_KEY,
            'ItemId': isbn,
            'ItemIdType': 'ISBN13',
            'output': 'js',
            'Version': '20131101',
            'Cover': 'Big'
        }
        
        response = requests.get(ALADIN_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('item'):
            item = data['item'][0]
            cover = item.get('cover')
            publisher = item.get('publisher')
            pub_date = item.get('pubDate')
            
            results.append({
                'title': title,
                'isbn': isbn,
                'cover': cover,
                'publisher': publisher,
                'pub_date': pub_date,
                'status': 'success'
            })
            print(f"  ✅ 정보 확인: {item.get('title')}")
            print(f"     표지: {cover}")
        else:
            # 알라딘에 없을 경우 기본 정보만 저장
            results.append({
                'title': title,
                'isbn': isbn,
                'cover': None,
                'status': 'not_found_in_aladin'
            })
            print(f"  ⚠️ 알라딘에서 상세 정보 못 찾음")
            
    except Exception as e:
        print(f"  ❌ 에러: {e}")
        # 에러 시에도 ISBN은 업데이트하도록
        results.append({
            'title': title,
            'isbn': isbn,
            'cover': None,
            'status': 'error'
        })

# SQL 생성
sql_lines = []
sql_lines.append("-- 수동 입력 ISBN 업데이트 (알라딘 메타데이터 포함)")
sql_lines.append(f"-- 처리 건수: {len(results)}권")
sql_lines.append("-- 생성일: 2026-01-19")
sql_lines.append("")

for result in results:
    title_escaped = result['title'].replace("'", "''")
    isbn_escaped = result['isbn']
    
    sql = f"""UPDATE childbook_items 
SET isbn = '{isbn_escaped}'"""
    
    if result.get('cover'):
        cover_escaped = result['cover'].replace("'", "''")
        sql += f",\n    image_url = '{cover_escaped}'"
    
    if result.get('publisher'):
        pub_escaped = result['publisher'].replace("'", "''")
        sql += f",\n    publisher = '{pub_escaped}'"
        
    sql += f"""
WHERE title = '{title_escaped}' 
  AND curation_tag = '겨울방학2026';
"""
    
    sql_lines.append(f"-- {result['title']}")
    sql_lines.append(sql)

# 파일 저장
filename = 'update_winter_isbn_manual.sql'
with open(filename, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))

print(f"\n✅ {filename} 파일 생성 완료!")
