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
            'Query': search_title,
            'QueryType': 'Title',
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
                
                if title_match and author_match:
                    matched_item = item
                    break
            
            # 매칭 실패 시 첫 번째 결과 사용 (제목만 일치)
            if not matched_item:
                for item in data_json['item']:
                    item_title = item.get('title', '')
                    if search_title.lower() in item_title.lower():
                        matched_item = item
                        break
            
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

# 실패 목록
if fail_count > 0:
    print(f"\n⚠️ 데이터를 찾지 못한 책 ({fail_count}권):")
    for result in results:
        if result['status'] != 'success':
            print(f"  - {result['year']}년: {result.get('korean_title') or result['original_title']} ({result['status']})")
