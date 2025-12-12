"""
판교 도서관 웹사이트 API 확인
"""
import requests
from bs4 import BeautifulSoup
import json

# 판교 도서관 웹사이트에서 '밤마다 환상축제' 검색
search_url = "https://www.snlib.go.kr/intro/menu/10041/program/30009/plusSearchResultDetail.do"

params = {
    "recKey": "1930855775",
    "bookKey": "1930855774",
    "publishFormCode": "BO"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("=" * 60)
print("판교 도서관 웹사이트에서 청구기호 정보 확인")
print("=" * 60)
print()

try:
    res = requests.get(search_url, params=params, headers=headers, timeout=30)
    res.raise_for_status()
    res.encoding = 'utf-8'
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 청구기호 찾기
    print("HTML에서 청구기호 찾기:")
    print("-" * 60)
    
    # 테이블에서 청구기호 찾기
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            for i, cell in enumerate(cells):
                text = cell.get_text(strip=True)
                if '청구기호' in text or '유 808.9' in text or 'ㅇ175ㅇ' in text or '204' in text:
                    print(f"발견: {text}")
                    # 같은 행의 모든 셀 출력
                    row_text = [c.get_text(strip=True) for c in cells]
                    print(f"전체 행: {row_text}")
                    print()
    
    # 스크립트 태그에서 JSON 데이터 찾기
    scripts = soup.find_all('script')
    for script in scripts:
        script_text = script.string
        if script_text and ('callno' in script_text.lower() or '청구기호' in script_text or '204' in script_text):
            print("스크립트에서 관련 내용 발견:")
            # 관련 부분만 출력 (너무 길면 잘라서)
            lines = script_text.split('\n')
            for line in lines:
                if 'callno' in line.lower() or '청구기호' in line or '204' in line or '808.9' in line:
                    print(f"  {line[:200]}")
            print()
    
    # data- 속성이나 id 속성에서 찾기
    elements_with_data = soup.find_all(attrs={'data-callno': True})
    if elements_with_data:
        print("data-callno 속성 발견:")
        for elem in elements_with_data:
            print(f"  {elem.get('data-callno')}")
        print()
    
    # 청구기호가 포함된 모든 텍스트 찾기
    all_text = soup.get_text()
    if '유 808.9-ㅇ175ㅇ-204' in all_text:
        print("✅ 전체 청구기호 '유 808.9-ㅇ175ㅇ-204' 발견!")
        # 주변 텍스트 출력
        idx = all_text.find('유 808.9-ㅇ175ㅇ-204')
        start = max(0, idx - 100)
        end = min(len(all_text), idx + 200)
        print(f"주변 텍스트:\n{all_text[start:end]}")
        print()
    
    # 총서 정보 찾기
    if '204' in all_text:
        print("'204' 관련 텍스트:")
        lines = all_text.split('\n')
        for i, line in enumerate(lines):
            if '204' in line:
                print(f"  {line.strip()}")
                # 앞뒤 몇 줄도 출력
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if j != i:
                        print(f"    {lines[j].strip()}")
                print()

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()






