"""
no_callno_items.csv의 항목들을 판교 도서관 웹사이트에서 검색하여
청구기호를 찾아 pangyo_callno에 업데이트
"""
from supabase_client import supabase
import csv
import requests
from bs4 import BeautifulSoup
import time
import re
import sys

print("=" * 60)
print("판교 도서관 웹사이트에서 청구기호 검색")
print("=" * 60)
print()

def search_callno_from_website(isbn: str, title: str = "") -> str:
    """
    판교 도서관 웹사이트에서 청구기호 검색
    ISBN 또는 제목으로 검색하여 청구기호를 찾습니다.
    
    Returns:
        청구기호 문자열 (예: '유 808.9-ㅇ175ㅇ-204'), 없으면 빈 문자열
    """
    try:
        # 성남시 도서관 통합자료검색 URL
        # 간략검색: plusSearchSimple.do
        # 검색 결과: plusSearchResult.do (POST 요청 또는 파라미터 필요)
        search_url = "https://www.snlib.go.kr/intro/menu/10041/program/30009/plusSearchSimple.do"
        
        # 제목이 있으면 제목으로 검색, 없으면 ISBN으로 검색
        search_keyword = title if title else isbn
        
        params = {
            "searchType": "SIMPLE",
            "searchCategory": "BOOK",
            "searchKey": "ALL",
            "searchKeyword": search_keyword,
            "searchLibrary": "",
            "searchPbLibrary": "ALL",
            "currentPageNo": "1",
            "searchRecordCount": "20"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        res = requests.get(search_url, params=params, headers=headers, timeout=30)
        res.raise_for_status()
        res.encoding = 'utf-8'
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 테이블에서 청구기호 찾기
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # 판교도서관 자료실 확인 및 청구기호 찾기
                for i, cell_text in enumerate(cell_texts):
                    if '[판교]' in cell_text or '판교' in cell_text:
                        # 다음 셀들에서 청구기호 찾기
                        for j in range(i, min(i+5, len(cell_texts))):
                            callno_text = cell_texts[j]
                            # 청구기호 패턴 찾기 (예: '유 808.9-ㅇ175ㅇ-204', '아 808.9-ㄷ36')
                            callno_match = re.search(r'[아유]\s*\d+\.?\d*[-]\S+', callno_text)
                            if callno_match:
                                return callno_match.group(0).strip()
        
        # 테이블에서 직접 청구기호 패턴 찾기
        page_text = soup.get_text()
        callno_matches = re.findall(r'[아유]\s*\d+\.?\d*[-]\S+', page_text)
        if callno_matches:
            # 판교 관련 텍스트 근처의 청구기호 찾기
            for match in callno_matches:
                match_pos = page_text.find(match)
                context = page_text[max(0, match_pos-50):min(len(page_text), match_pos+50)]
                if '판교' in context:
                    return match.strip()
        
        return ""
        
    except Exception as e:
        return ""

# CSV 파일 읽기
csv_filename = "no_callno_items.csv"
print(f"1. CSV 파일 읽기: {csv_filename}")

items_to_search = []
try:
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            child_id = row.get('id', '').strip()
            isbn = row.get('isbn', '').strip()
            title = row.get('title', '').strip()
            
            if child_id and (isbn or title):
                items_to_search.append({
                    'child_id': int(child_id),
                    'isbn': isbn,
                    'title': title
                })
    
    print(f"   [OK] {len(items_to_search):,}개 항목 로드됨")
except Exception as e:
    print(f"   [ERROR] 오류: {e}")
    sys.exit(1)

if len(items_to_search) == 0:
    print("   [WARN] 처리할 항목이 없습니다.")
    sys.exit(0)

print()

# 웹사이트에서 검색하여 청구기호 찾기
print("2. 판교 도서관 웹사이트에서 청구기호 검색 중...")
print("   ⚠️  웹사이트 검색이므로 시간이 오래 걸릴 수 있습니다.")
print()

success_count = 0
fail_count = 0
not_found_count = 0

for idx, item in enumerate(items_to_search):
    child_id = item['child_id']
    isbn = item['isbn']
    title = item['title']
    
    # 웹사이트에서 청구기호 검색
    callno = search_callno_from_website(isbn, title)
    
    if callno and len(callno.strip()) > 0:
        try:
            supabase.table("childbook_items").update({
                "pangyo_callno": callno.strip()
            }).eq("id", child_id).execute()
            success_count += 1
        except Exception as e:
            fail_count += 1
            if fail_count <= 5:
                print(f"   [ERROR] ID {child_id} 업데이트 실패: {e}")
    else:
        not_found_count += 1
    
    # 진행 상황 출력 (50개마다)
    if (idx + 1) % 50 == 0:
        print(f"   진행 중: {idx + 1}/{len(items_to_search)} (성공: {success_count}, 실패: {fail_count}, 찾지못함: {not_found_count})")
        sys.stdout.flush()
    
    # API 호출 제한 고려 (초당 1회 정도)
    time.sleep(1)

print()
print("=" * 60)
print("[OK] 완료!")
print("-" * 60)
print(f"총 처리: {len(items_to_search):,}개")
print(f"성공 (청구기호 찾음): {success_count:,}개")
print(f"실패: {fail_count:,}개")
print(f"찾지 못함: {not_found_count:,}개")
print("=" * 60)

