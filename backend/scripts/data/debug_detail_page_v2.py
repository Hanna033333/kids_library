import requests
from bs4 import BeautifulSoup
import re

# 테스트: 상세 페이지 HTML 구조 확인
DETAIL_URL = "https://www.snlib.go.kr/pg/menu/10519/program/30009/plusSearchResultDetail.do"

# 나는 오늘도 감정식당에 가요
params = {
    'recKey': '1949734267',
    'bookKey': '1949734269'
}

response = requests.get(DETAIL_URL, params=params, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

output = []
output.append("=== 상세 페이지 HTML 구조 분석 ===\n")

# 모든 테이블 찾기
tables = soup.select('table')
output.append(f"테이블 개수: {len(tables)}\n")

# 표준번호 찾기 - 여러 방법 시도
output.append("=== 방법 1: th 태그에서 '표준번호' 찾기 ===")
th_elements = soup.select('th')
for i, th in enumerate(th_elements):
    if '표준번호' in th.get_text():
        output.append(f"찾음! th 인덱스: {i}")
        output.append(f"th 텍스트: {th.get_text(strip=True)}")
        td = th.find_next_sibling('td')
        if td:
            output.append(f"td 텍스트: {td.get_text(strip=True)}")
        output.append("")

output.append("\n=== 방법 2: dt 태그에서 '표준번호' 찾기 ===")
dt_elements = soup.select('dt')
for i, dt in enumerate(dt_elements):
    if '표준번호' in dt.get_text():
        output.append(f"찾음! dt 인덱스: {i}")
        output.append(f"dt 텍스트: {dt.get_text(strip=True)}")
        dd = dt.find_next_sibling('dd')
        if dd:
            output.append(f"dd 텍스트: {dd.get_text(strip=True)}")
        output.append("")

output.append("\n=== 방법 3: 모든 텍스트에서 'ISBN' 검색 ===")
all_text = soup.get_text()
isbn_matches = re.findall(r'ISBN[:\s-]*(\d{13}|\d{10})', all_text, re.IGNORECASE)
if isbn_matches:
    output.append(f"찾은 ISBN: {isbn_matches}")
else:
    output.append("ISBN 못 찾음")

output.append("\n=== 방법 4: class나 id로 찾기 ===")
# 표준번호가 있는 영역의 부모 요소 찾기
for elem in soup.find_all(string=re.compile('표준번호')):
    output.append(f"요소: {elem.parent.name}")
    output.append(f"클래스: {elem.parent.get('class')}")
    output.append(f"부모: {elem.parent.parent.name}")
    output.append(f"전체 HTML:")
    output.append(elem.parent.parent.prettify()[:1000])
    output.append("")

# 파일로 저장
with open('detail_page_debug.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("✅ detail_page_debug.txt 파일로 저장 완료!")
