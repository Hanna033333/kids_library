"""
childbook_items의 ISBN과 library_items의 isbn13이 같지만 서로 다른 책인 경우 찾기
"""
from supabase_client import supabase
import csv

print("=" * 60)
print("ISBN은 같지만 서로 다른 책 찾기")
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

# 2) library_items에서 ISBN-13으로 인덱스 생성 (제목, 저자 포함)
print("2. library_items에서 ISBN-13 인덱스 생성 중...")
library_by_isbn = {}
page = 0
page_size = 1000

while True:
    res = supabase.table("library_items").select("isbn13,title,author,callno").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
    for item in res.data:
        isbn13 = item.get("isbn13")
        if isbn13:
            # ISBN-13 정규화 (숫자만 추출)
            isbn_normalized = ''.join(filter(str.isdigit, str(isbn13)))
            if len(isbn_normalized) == 13:
                # 같은 ISBN이 여러 개 있을 수 있으므로 리스트로 저장
                if isbn_normalized not in library_by_isbn:
                    library_by_isbn[isbn_normalized] = []
                library_by_isbn[isbn_normalized].append(item)
    
    if len(res.data) < page_size:
        break
    page += 1

print(f"   [OK] library_items ISBN-13: {len(library_by_isbn):,}개 고유 ISBN")
print()

# 3) 매칭 확인 - ISBN은 같지만 제목이나 저자가 다른 경우 찾기
print("3. ISBN은 같지만 서로 다른 책 찾기...")
mismatched_items = []

for child_item in child_items_with_isbn:
    child_isbn = child_item.get("isbn")
    if not child_isbn:
        continue
    
    # childbook_items의 ISBN 정규화
    child_isbn_normalized = ''.join(filter(str.isdigit, str(child_isbn)))
    
    # ISBN-13 형식 확인
    matched_library_items = None
    
    if len(child_isbn_normalized) == 13:
        # ISBN-13 직접 매칭
        matched_library_items = library_by_isbn.get(child_isbn_normalized)
    elif len(child_isbn_normalized) == 10:
        # ISBN-10을 ISBN-13으로 변환하여 매칭 시도
        isbn13_from_10 = "978" + child_isbn_normalized[:9]
        checksum = sum(int(digit) * (3 if i % 2 == 1 else 1) for i, digit in enumerate(isbn13_from_10[:12])) % 10
        checksum = (10 - checksum) % 10
        isbn13_from_10 = isbn13_from_10[:12] + str(checksum)
        matched_library_items = library_by_isbn.get(isbn13_from_10)
    
    if matched_library_items:
        # 같은 ISBN을 가진 library_items 항목들과 비교
        child_title = (child_item.get("title") or "").strip()
        child_author = (child_item.get("author") or "").strip()
        
        # 제목이나 저자가 다른 경우 찾기
        is_mismatched = False
        matched_lib_item = None
        
        for lib_item in matched_library_items:
            lib_title = (lib_item.get("title") or "").strip()
            lib_author = (lib_item.get("author") or "").strip()
            
            # 제목이 다르거나 저자가 다른 경우
            if child_title and lib_title and child_title != lib_title:
                is_mismatched = True
                matched_lib_item = lib_item
                break
            elif child_author and lib_author and child_author != lib_author:
                # 저자 비교는 더 유연하게 (일부만 포함되어도 OK로 간주하지 않음)
                # 완전히 다른 경우만 체크
                if child_author not in lib_author and lib_author not in child_author:
                    is_mismatched = True
                    matched_lib_item = lib_item
                    break
        
        if is_mismatched and matched_lib_item:
            mismatched_items.append({
                'child_id': child_item.get('id'),
                'child_isbn': child_isbn,
                'child_title': child_title,
                'child_author': child_author,
                'child_publisher': child_item.get('publisher', ''),
                'lib_isbn13': matched_lib_item.get('isbn13'),
                'lib_title': matched_lib_item.get('title', ''),
                'lib_author': matched_lib_item.get('author', ''),
                'lib_callno': matched_lib_item.get('callno', '')
            })
    
    # 진행 상황 출력 (1000개마다)
    if len(mismatched_items) > 0 and len(mismatched_items) % 100 == 0:
        print(f"   진행 중: {len(mismatched_items):,}개 불일치 발견...")

print(f"   [OK] 확인 완료")
print()

# 4) 결과 출력
print("=" * 60)
print("결과")
print("=" * 60)
print(f"ISBN은 같지만 서로 다른 책: {len(mismatched_items):,}개")
print()

# 5) CSV 파일로 저장
if len(mismatched_items) > 0:
    csv_filename = "mismatched_isbn_books.csv"
    print(f"CSV 파일로 저장 중: {csv_filename}")
    
    fieldnames = ['child_id', 'child_isbn', 'child_title', 'child_author', 'child_publisher', 
                  'lib_isbn13', 'lib_title', 'lib_author', 'lib_callno']
    
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in mismatched_items:
            writer.writerow(item)
    
    print(f"✅ 저장 완료: {csv_filename}")
    print(f"   총 {len(mismatched_items):,}개 항목")
else:
    print("✅ 불일치 항목이 없습니다!")

print()
print("=" * 60)

