import requests
from bs4 import BeautifulSoup
import time
import re
import sys
import io

# 콘솔 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "https://www.snlib.go.kr/pg/plusSearchResultList.do"

# 크롤링 대상 도서 목록 (제목, 저자, ISBN - ISBN은 DB 업데이트용 키)
target_books = [
    {"title": "나의 특별한 도시락", "author": "체리 모", "isbn": "9791169942874"},
    {"title": "워터 프로텍터", "author": "캐롤 린드스트롬", "isbn": "9791168254114"},
    {"title": "우리는 패배하지 않아", "author": "콰미 알렉산더", "isbn": "9788961707978"},
    {"title": "증기기관차 대륙을 달리다", "author": "브라이언 플로카", "isbn": "9788994407753"},
    {"title": "빨강 파랑 강아지 공", "author": "크리스 라쉬카", "isbn": "9788983090324"},
    {"title": "할아버지 댁 창문", "author": "노턴 저스터", "isbn": "9791125304562"}
]

def normalize(text):
    if not text: return ""
    text = re.sub(r'\(.*?\)|\[.*?\]', '', text)
    text = re.sub(r'[\s\W_]+', '', text).lower()
    return text

print(f"🚀 판교도서관 청구기호 크롤링 시작... (총 {len(target_books)}권)")

sql_lines = []
sql_lines.append("-- 판교도서관 청구기호 업데이트 (크롤링 결과)")
sql_lines.append("-- 생성일: 2026-02-06")
sql_lines.append("")

success_count = 0
fail_count = 0

for i, book in enumerate(target_books, 1):
    title = book['title']
    author = book['author']
    isbn = book['isbn']
    
    print(f"[{i}/{len(target_books)}] {title} (저자: {author}) 검색 중...")
    
    found_callno = None
    
    try:
        params = {
            'searchKeyword': title,
            'searchType': 'SIMPLE',
            'searchCategory': 'BOOK',
            'searchLibraryArr': 'MP',
            'searchKey': 'ALL',
            'topSearchType': 'BOOK'
        }
        
        response = requests.get(BASE_URL, params=params, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            result_items = soup.select('ul.resultList > li')
            
            if result_items:
                norm_target_title = normalize(title)
                norm_target_author = normalize(author)
                
                for item in result_items:
                    # 제목 매칭 확인
                    title_elem = item.select_one('.tit a')
                    result_title = title_elem.get_text(strip=True) if title_elem else ""
                    norm_result_title = normalize(result_title)
                    
                    if norm_target_title not in norm_result_title:
                        continue
                        
                    # 저자 매칭 확인 (옵션)
                    item_text = item.get_text(strip=True)
                    norm_item_text = normalize(item_text)
                    
                    if norm_target_author not in norm_item_text:
                        print(f"  ⚠️ 저자 불일치: {result_title}")
                        # continue # 저자 불일치시 건너뛸지 여부 결정 (일단 진행해봄)
                    
                    # 청구기호 추출
                    dd_elements = item.select('dl dd')
                    for dd in dd_elements:
                        text = dd.get_text(strip=True)
                        if '청구기호' in text:
                            parts = text.split('청구기호')
                            if len(parts) > 1:
                                candidate = parts[-1].replace(':', '').strip()
                                # 불필요한 텍스트 제거 ('위치출력', '미리보기' 등)
                                clean_candidate = candidate.split('위치출력')[0].strip()
                                found_callno = clean_candidate
                                break
                    
                    if found_callno:
                        print(f"  ✅ 찾음: {found_callno}")
                        break
            else:
                print("  ❌ 검색 결과 없음")
        else:
            print(f"  ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ 에러: {e}")
    
    if found_callno:
        success_count += 1
        sql = f"UPDATE childbook_items SET pangyo_callno = '{found_callno}' WHERE isbn = '{isbn}';"
        sql_lines.append(f"-- {title}")
        sql_lines.append(sql)
    else:
        fail_count += 1
        sql_lines.append(f"-- 실패: {title} (검색 실패)")
    
    time.sleep(1.0)

# SQL 파일 저장
with open('update_missing_caldecott_callno.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))

print("\n" + "="*50)
print(f"✅ 성공: {success_count}권")
print(f"❌ 실패: {fail_count}권")
print("✅ update_missing_caldecott_callno.sql 파일 생성 완료")
print("="*50)
