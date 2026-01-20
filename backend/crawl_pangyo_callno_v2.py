import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# JSON 파일 읽기
with open('winter_books_clean.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

print(f"🔍 판교도서관 청구기호 크롤링 시작 (총 {len(books)}권)")
print()

# 판교도서관 검색 URL (성남시립도서관 시스템)
BASE_URL = "https://www.snlib.go.kr/pg/plusSearchResultList.do"

results = []
success_count = 0
fail_count = 0

for i, book in enumerate(books, 1):
    title = book['서명']
    author = book['저자'].split()[0] if book['저자'] else ''
    
    print(f"[{i}/{len(books)}] {title}")
    
    try:
        # 검색 파라미터
        params = {
            'searchKeyword': title,
            'searchType': 'SIMPLE',
            'searchCategory': 'BOOK',
            'searchLibraryArr': 'MP',  # 판교도서관
            'searchKey': 'ALL',
            'topSearchType': 'BOOK'
        }
        
        # 검색 요청
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 검색 결과에서 첫 번째 책 찾기
        result_list = soup.select('ul.resultList > li')
        
        if result_list:
            first_result = result_list[0]
            
            # 청구기호 찾기: dd 요소 중 "청구기호:" 텍스트 포함하는 것
            dd_elements = first_result.select('dl dd')
            callno = None
            
            for dd in dd_elements:
                text = dd.get_text(strip=True)
                if '청구기호:' in text:
                    # "청구기호:" 뒤의 텍스트 추출
                    callno = text.replace('청구기호:', '').strip()
                    # "위치출력" 등 불필요한 텍스트 제거
                    callno = callno.split('위치출력')[0].strip()
                    break
            
            if callno:
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
                    'status': 'no_callno'
                })
                fail_count += 1
                print(f"  ⚠️ 검색 결과 있으나 청구기호 없음")
        else:
            results.append({
                'title': title,
                'author': author,
                'callno': None,
                'status': 'not_found'
            })
            fail_count += 1
            print(f"  ❌ 검색 결과 없음 (신간 미등록 가능성)")
        
        # 요청 간격 (서버 부하 방지)
        time.sleep(1.5)
        
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
print(f"📊 성공률: {success_count/len(books)*100:.1f}%")
print("="*50)

# 결과 저장
with open('winter_books_callno_results.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(books),
        'success': success_count,
        'fail': fail_count,
        'results': results
    }, f, ensure_ascii=False, indent=2)

print("\n✅ winter_books_callno_results.json 파일로 저장 완료!")

# UPDATE SQL 생성
if success_count > 0:
    sql_lines = []
    sql_lines.append("-- 겨울방학 도서 청구기호 업데이트")
    sql_lines.append(f"-- 크롤링 결과: {success_count}/{len(books)}권 성공")
    sql_lines.append("-- 생성일: 2026-01-19")
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
            sql_lines.append(f"-- {result['title']}: {result['callno']}")
            sql_lines.append(sql)
    
    # 확인 쿼리
    sql_lines.append("")
    sql_lines.append("-- 확인 쿼리")
    sql_lines.append("SELECT title, pangyo_callno")
    sql_lines.append("FROM childbook_items")
    sql_lines.append("WHERE curation_tag = '겨울방학2026'")
    sql_lines.append("  AND pangyo_callno IS NOT NULL;")
    
    with open('update_winter_callno.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    
    print(f"✅ update_winter_callno.sql 파일 생성 완료! ({success_count}개 UPDATE 문)")
else:
    print("⚠️ 성공한 결과가 없어 SQL 파일을 생성하지 않았습니다.")

# 실패 목록 출력
if fail_count > 0:
    print(f"\n⚠️ 청구기호를 찾지 못한 책 ({fail_count}권):")
    for result in results:
        if result['status'] != 'success':
            print(f"  - {result['title']} ({result['status']})")
