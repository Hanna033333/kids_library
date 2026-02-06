import json
import requests
import sys
import os

# config에서 API 키 가져오기
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.config import ALADIN_TTB_KEY

ALADIN_URL = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"

# User provided ISBN list
target_books = [
    {"year": 2025, "isbn": "9791169942874"},
    {"year": 2021, "isbn": "9791168254114"},
    {"year": 2020, "isbn": "9788961707978"},
    {"year": 2014, "isbn": "9788994407753"},
    {"year": 2012, "isbn": "9788983090324"},
    {"year": 2006, "isbn": "9791125304562"}
]

sql_lines = []
sql_lines.append("-- 추가된 칼데콧 수상작 (사용자 제공 ISBN 기반)")
sql_lines.append(f"-- 생성일: 2026-02-06")
sql_lines.append("")

print(f"🔍 알라딘 API로 {len(target_books)}권의 데이터 조회를 시작합니다...")

for book in target_books:
    isbn = book['isbn']
    year = book['year']
    
    try:
        params = {
            'ttbkey': ALADIN_TTB_KEY,
            'ItemId': isbn,
            'ItemIdType': 'ISBN13',
            'output': 'js',
            'Version': '20131101',
            'Cover': 'Big'  # 고화질 표지 요청
        }
        
        response = requests.get(ALADIN_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'item' in data and data['item']:
            item = data['item'][0]
            title = item.get('title', '').replace("'", "''")
            author = item.get('author', '').replace("'", "''")
            publisher = item.get('publisher', '').replace("'", "''")
            image_url = item.get('cover', '').replace("sum", "500") # 고화질 변환 시도
            if not image_url:
                image_url = item.get('cover', '')
                
            print(f"✅ {year}년: {title} (ISBN: {isbn})")
            
            # SQL 생성
            sql = f"""-- {year}년: {title}
INSERT INTO childbook_items (title, author, publisher, isbn, image_url, pangyo_callno, curation_tag, category, age, is_hidden)
VALUES ('{title}', '{author}', '{publisher}', '{isbn}', '{image_url}', NULL, 'caldecott', '그림책', '5세부터', false)
ON CONFLICT (isbn) DO UPDATE SET
  curation_tag = CASE 
    WHEN childbook_items.curation_tag IS NULL OR childbook_items.curation_tag = '' THEN EXCLUDED.curation_tag
    WHEN childbook_items.curation_tag LIKE '%' || EXCLUDED.curation_tag || '%' THEN childbook_items.curation_tag
    ELSE childbook_items.curation_tag || ', ' || EXCLUDED.curation_tag
  END,
  image_url = COALESCE(EXCLUDED.image_url, childbook_items.image_url);
"""
            sql_lines.append(sql)
            
        else:
            print(f"❌ {year}년 ISBN {isbn}: 검색 결과 없음")
            
    except Exception as e:
        print(f"❌ {year}년 ISBN {isbn}: 에러 발생 - {e}")

# SQL 파일 저장
output_file = 'insert_missing_caldecott.sql'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))

print(f"\n✅ {output_file} 생성 완료")
