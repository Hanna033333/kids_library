"""
childbook_items에 ISBN이 있지만 library_items에서 매칭되지 않는 항목 찾기
"""
from supabase_client import supabase
import csv

print("=" * 60)
print("ISBN 매칭되지 않는 항목 찾기")
print("=" * 60)
print()

# 1) childbook_items에서 ISBN이 있는 항목 조회
print("1. childbook_items에서 ISBN이 있는 항목 조회 중...")
child_items_with_isbn = []
page = 0
page_size = 1000

while True:
    res = supabase.table("childbook_items").select("id,isbn,title,author,publisher").not_.is_("isbn", "null").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
    for item in res.data:
        isbn = item.get("isbn")
        if isbn and len(str(isbn).strip()) > 0:
            child_items_with_isbn.append(item)
    
    if len(res.data) < page_size:
        break
    page += 1

print(f"   [OK] ISBN이 있는 항목: {len(child_items_with_isbn):,}개")
print()

# 2) library_items에서 ISBN-13 인덱스 생성
print("2. library_items에서 ISBN-13 인덱스 생성 중...")
library_isbn_set = set()
page = 0
page_size = 1000

while True:
    res = supabase.table("library_items").select("isbn13").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
    for item in res.data:
        isbn13 = item.get("isbn13")
        if isbn13:
            # ISBN-13 정규화 (숫자만 추출)
            isbn_normalized = ''.join(filter(str.isdigit, str(isbn13)))
            if len(isbn_normalized) == 13:
                library_isbn_set.add(isbn_normalized)
    
    if len(res.data) < page_size:
        break
    page += 1

print(f"   [OK] library_items ISBN-13: {len(library_isbn_set):,}개")
print()

# 3) 매칭되지 않는 항목 찾기
print("3. 매칭 확인 중...")
unmatched_items = []

for child_item in child_items_with_isbn:
    child_isbn = child_item.get("isbn")
    if not child_isbn:
        continue
    
    # childbook_items의 ISBN 정규화
    child_isbn_normalized = ''.join(filter(str.isdigit, str(child_isbn)))
    
    # ISBN-13 형식 확인
    matched = False
    
    if len(child_isbn_normalized) == 13:
        # ISBN-13 직접 매칭
        if child_isbn_normalized in library_isbn_set:
            matched = True
    elif len(child_isbn_normalized) == 10:
        # ISBN-10을 ISBN-13으로 변환하여 매칭 시도
        isbn13_from_10 = "978" + child_isbn_normalized[:9]
        checksum = sum(int(digit) * (3 if i % 2 == 1 else 1) for i, digit in enumerate(isbn13_from_10[:12])) % 10
        checksum = (10 - checksum) % 10
        isbn13_from_10 = isbn13_from_10[:12] + str(checksum)
        
        if isbn13_from_10 in library_isbn_set:
            matched = True
    
    if not matched:
        unmatched_items.append(child_item)
    
    # 진행 상황 출력 (1000개마다)
    if len(unmatched_items) % 1000 == 0 and len(unmatched_items) > 0:
        print(f"   진행 중: {len(unmatched_items):,}개 매칭 안됨...")

print(f"   [OK] 매칭 확인 완료")
print()

# 4) 결과 출력
print("=" * 60)
print("결과")
print("=" * 60)
print(f"childbook_items에 ISBN이 있는 항목: {len(child_items_with_isbn):,}개")
print(f"library_items에 매칭되는 항목: {len(child_items_with_isbn) - len(unmatched_items):,}개")
print(f"매칭되지 않는 항목: {len(unmatched_items):,}개")
print()

# 5) CSV 파일로 저장
csv_filename = "unmatched_isbn_items.csv"
print(f"CSV 파일로 저장 중: {csv_filename}")

fieldnames = ['id', 'isbn', 'title', 'author', 'publisher', 'pangyo_callno']

with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for item in unmatched_items:
        row = {
            'id': item.get('id', ''),
            'isbn': item.get('isbn', ''),
            'title': item.get('title', ''),
            'author': item.get('author', ''),
            'publisher': item.get('publisher', ''),
            'pangyo_callno': item.get('pangyo_callno', '')
        }
        writer.writerow(row)

print(f"✅ 저장 완료: {csv_filename}")
print(f"   총 {len(unmatched_items):,}개 항목")
print()
print("=" * 60)

