import json
import time
import requests
from bs4 import BeautifulSoup

# JSON 파일 읽기
with open('winter_books_clean.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

print(f"🔍 판교도서관 청구기호 크롤링 시작 (총 {len(books)}권)")
print()

# 판교도서관 검색 URL
SEARCH_URL = "https://www.pangyolib.or.kr/intro/search/searchList.do"

results = []
success_count = 0
fail_count = 0

for i, book in enumerate(books, 1):
    title = book['서명']
    author = book['저자'].split()[0] if book['저자'] else ''  # 첫 번째 저자명만
    
    print(f"[{i}/{len(books)}] {title}")
    
    try:
        # 검색 요청
        params = {
            'searchField': 'TITLE',
            'searchText': title,
            'searchLibraryArr': 'MA'  # 판교도서관
        }
        
        response = requests.get(SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 검색 결과에서 청구기호 찾기
        # (실제 HTML 구조에 맞게 수정 필요)
        callno_element = soup.select_one('.callno, .call_no, [class*="callno"]')
        
        if callno_element:
            callno = callno_element.text.strip()
            results.append({
                'title': title,
                'author': author,
                'callno': callno,
                'status': 'success'
            })
            success_count += 1
            print(f"  ✅ 청구기호: {callno}")
        else:
            results.append({
                'title': title,
                'author': author,
                'callno': None,
                'status': 'not_found'
            })
            fail_count += 1
            print(f"  ❌ 청구기호 없음")
        
        # 요청 간격 (서버 부하 방지)
        time.sleep(1)
        
    except Exception as e:
        results.append({
            'title': title,
            'author': author,
            'callno': None,
            'status': 'error',
            'error': str(e)
        })
        fail_count += 1
        print(f"  ❌ 에러: {e}")
        time.sleep(2)

print()
print("="*50)
print(f"✅ 성공: {success_count}권")
print(f"❌ 실패: {fail_count}권")
print("="*50)

# 결과 저장
with open('winter_books_callno_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n✅ winter_books_callno_results.json 파일로 저장 완료!")

# UPDATE SQL 생성
if success_count > 0:
    sql_lines = []
    sql_lines.append("-- 겨울방학 도서 청구기호 업데이트")
    sql_lines.append("-- 크롤링 결과 기반")
    sql_lines.append("")
    
    for result in results:
        if result['status'] == 'success' and result['callno']:
            title_escaped = result['title'].replace("'", "''")
            callno_escaped = result['callno'].replace("'", "''")
            
            sql = f"""UPDATE childbook_items 
SET pangyo_callno = '{callno_escaped}'
WHERE title = '{title_escaped}' 
  AND curation_tag = '겨울방학2026';
"""
            sql_lines.append(f"-- {result['title']}")
            sql_lines.append(sql)
    
    with open('update_winter_callno.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    
    print("✅ update_winter_callno.sql 파일 생성 완료!")
