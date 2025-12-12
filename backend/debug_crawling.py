"""
크롤링 디버깅 - 검색 결과 페이지 구조 확인
"""
import requests
from bs4 import BeautifulSoup
import re

# '밤마다 환상축제' 검색
search_url = "https://www.snlib.go.kr/intro/menu/10041/program/30009/plusSearchResult.do"

params = {
    "searchType": "SIMPLE",
    "searchCategory": "BOOK",
    "searchKey": "ALL",
    "searchKeyword": "밤마다 환상축제",
    "searchLibrary": "",
    "searchPbLibrary": "ALL",
    "currentPageNo": "1",
    "searchRecordCount": "20"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("=" * 60)
print("검색 결과 페이지 구조 확인")
print("=" * 60)
print()

try:
    res = requests.get(search_url, params=params, headers=headers, timeout=15)
    res.raise_for_status()
    res.encoding = 'utf-8'
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # HTML 저장 (디버깅용)
    with open('search_result.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("✅ HTML 저장됨: search_result.html")
    print()
    
    # 테이블 찾기
    tables = soup.find_all('table')
    print(f"테이블 개수: {len(tables)}")
    print()
    
    for i, table in enumerate(tables):
        print(f"테이블 {i+1}:")
        rows = table.find_all('tr')
        print(f"  행 개수: {len(rows)}")
        
        # 처음 몇 행 확인
        for j, row in enumerate(rows[:5]):
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            print(f"  행 {j+1}: {cell_texts}")
            
            # 판교도서관 관련 텍스트 찾기
            for text in cell_texts:
                if '판교' in text or '청구기호' in text or '유 808.9' in text or '204' in text:
                    print(f"    ⭐ 발견: {text}")
        print()
    
    # 전체 텍스트에서 청구기호 패턴 찾기
    all_text = soup.get_text()
    
    # '유 808.9-ㅇ175ㅇ-204' 패턴 찾기
    patterns = [
        r'유\s+808\.9-ㅇ175ㅇ-204',
        r'유\s+808\.9-ㅇ175ㅇ-\d+',
        r'[유아]\s+\d+[.\d]*-[가-힣\d]+-\d+',
    ]
    
    print("청구기호 패턴 검색:")
    for pattern in patterns:
        matches = re.findall(pattern, all_text)
        if matches:
            print(f"  패턴 '{pattern}': {len(matches)}개 발견")
            for match in matches[:3]:
                print(f"    - {match}")
        else:
            print(f"  패턴 '{pattern}': 발견 안 됨")
    print()
    
    # '204' 포함된 텍스트 찾기
    lines = all_text.split('\n')
    print("'204' 포함된 줄:")
    for line in lines:
        if '204' in line and ('유' in line or '808.9' in line or '청구기호' in line):
            print(f"  {line.strip()[:100]}")

except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc()






