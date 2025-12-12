"""
pangyo_callno가 없는 항목들을 원인별로 분석
"""
from supabase_client import supabase

print("=" * 60)
print("pangyo_callno가 없는 항목 원인 분석")
print("=" * 60)
print()

# 1) pangyo_callno가 없는 childbook_items 조회
print("1. pangyo_callno가 없는 항목 조회 중...")
child_items_no_callno = []
page = 0
page_size = 1000

while True:
    res = supabase.table("childbook_items").select("id,isbn,title,author,pangyo_callno").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
    for item in res.data:
        pangyo_callno = item.get("pangyo_callno")
        has_pangyo_callno = pangyo_callno and len(str(pangyo_callno).strip()) > 0
        
        if not has_pangyo_callno:
            child_items_no_callno.append(item)
    
    if len(res.data) < page_size:
        break
    page += 1

print(f"   [OK] pangyo_callno가 없는 항목: {len(child_items_no_callno):,}개")
print()

# 2) library_items에서 ISBN-13 인덱스 생성 (제목, 저자 포함)
print("2. library_items 데이터 로드 중...")
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
            isbn_normalized = ''.join(filter(str.isdigit, str(isbn13)))
            if len(isbn_normalized) == 13:
                if isbn_normalized not in library_by_isbn:
                    library_by_isbn[isbn_normalized] = []
                library_by_isbn[isbn_normalized].append(item)
    
    if len(res.data) < page_size:
        break
    page += 1

print(f"   [OK] library_items ISBN-13: {len(library_by_isbn):,}개 고유 ISBN")
print()

# 3) 원인별 분류
print("3. 원인별 분류 중...")
print()

category1_no_isbn_in_library = []  # library_items에 ISBN 없는 책
category2_isbn_match_but_title_author_diff = []  # ISBN은 있는데 제목/저자가 맞지 않음
category3_other = []  # 그 외

for idx, child_item in enumerate(child_items_no_callno):
    child_id = child_item.get("id")
    child_isbn = child_item.get("isbn")
    child_title = (child_item.get("title") or "").strip()
    child_author = (child_item.get("author") or "").strip()
    
    # ISBN 정규화
    child_isbn_normalized = None
    if child_isbn:
        child_isbn_normalized = ''.join(filter(str.isdigit, str(child_isbn)))
        if len(child_isbn_normalized) == 10:
            # ISBN-10을 ISBN-13으로 변환
            isbn13_from_10 = "978" + child_isbn_normalized[:9]
            checksum = sum(int(digit) * (3 if i % 2 == 1 else 1) for i, digit in enumerate(isbn13_from_10[:12])) % 10
            checksum = (10 - checksum) % 10
            child_isbn_normalized = isbn13_from_10[:12] + str(checksum)
    
    # 분류
    if not child_isbn or not child_isbn_normalized or len(child_isbn_normalized) != 13:
        # ISBN이 없거나 형식이 맞지 않음
        category3_other.append({
            'id': child_id,
            'reason': 'ISBN 없음 또는 형식 오류',
            'isbn': child_isbn
        })
    elif child_isbn_normalized not in library_by_isbn:
        # library_items에 해당 ISBN이 없음
        category1_no_isbn_in_library.append({
            'id': child_id,
            'isbn': child_isbn,
            'title': child_title
        })
    else:
        # library_items에 ISBN이 있음 - 제목/저자 확인
        lib_items = library_by_isbn[child_isbn_normalized]
        matched = False
        
        for lib_item in lib_items:
            lib_title = (lib_item.get("title") or "").strip()
            lib_author = (lib_item.get("author") or "").strip()
            
            # 제목이 정확히 일치하는지 확인
            if child_title and lib_title and child_title == lib_title:
                matched = True
                break
            # 저자가 포함되어 있는지 확인 (유연한 매칭)
            elif child_author and lib_author:
                # 저자 이름의 주요 부분이 포함되어 있으면 OK로 간주
                child_author_clean = child_author.split('|')[0].split(',')[0].strip()
                lib_author_clean = lib_author.split(';')[0].split(',')[0].strip()
                if child_author_clean and lib_author_clean and child_author_clean in lib_author_clean:
                    matched = True
                    break
        
        if not matched:
            # ISBN은 있지만 제목/저자가 맞지 않음
            category2_isbn_match_but_title_author_diff.append({
                'id': child_id,
                'isbn': child_isbn,
                'child_title': child_title,
                'child_author': child_author,
                'lib_title': lib_items[0].get("title", "") if lib_items else "",
                'lib_author': lib_items[0].get("author", "") if lib_items else ""
            })
        else:
            # 매칭되었는데도 pangyo_callno가 없는 경우 (이상한 경우)
            category3_other.append({
                'id': child_id,
                'reason': 'ISBN/제목/저자 매칭됨에도 pangyo_callno 없음',
                'isbn': child_isbn
            })
    
    # 진행 상황 출력 (500개마다)
    if (idx + 1) % 500 == 0:
        print(f"   진행 중: {idx + 1}/{len(child_items_no_callno)}")

print()

# 4) 결과 출력
print("=" * 60)
print("분석 결과")
print("=" * 60)
print()
print(f"총 pangyo_callno 없는 항목: {len(child_items_no_callno):,}개")
print()
print(f"1. library_items에 ISBN 없는 책: {len(category1_no_isbn_in_library):,}개 ({len(category1_no_isbn_in_library)/len(child_items_no_callno)*100:.1f}%)")
print(f"2. ISBN은 있는데 제목/저자가 맞지 않음: {len(category2_isbn_match_but_title_author_diff):,}개 ({len(category2_isbn_match_but_title_author_diff)/len(child_items_no_callno)*100:.1f}%)")
print(f"3. 그 외의 이유: {len(category3_other):,}개 ({len(category3_other)/len(child_items_no_callno)*100:.1f}%)")
print()

# 세부 정보 출력
if len(category1_no_isbn_in_library) > 0:
    print("=" * 60)
    print("1. library_items에 ISBN 없는 책 (샘플 5개)")
    print("=" * 60)
    for item in category1_no_isbn_in_library[:5]:
        print(f"ID: {item['id']}, ISBN: {item['isbn']}, 제목: {item['title'][:50]}")

if len(category2_isbn_match_but_title_author_diff) > 0:
    print()
    print("=" * 60)
    print("2. ISBN은 있는데 제목/저자가 맞지 않음 (샘플 5개)")
    print("=" * 60)
    for item in category2_isbn_match_but_title_author_diff[:5]:
        print(f"ID: {item['id']}, ISBN: {item['isbn']}")
        print(f"  childbook: {item['child_title'][:40]} / {item['child_author'][:30]}")
        print(f"  library:   {item['lib_title'][:40]} / {item['lib_author'][:30]}")

if len(category3_other) > 0:
    print()
    print("=" * 60)
    print("3. 그 외의 이유 (샘플 5개)")
    print("=" * 60)
    for item in category3_other[:5]:
        print(f"ID: {item['id']}, 이유: {item['reason']}, ISBN: {item.get('isbn', 'N/A')}")

print()
print("=" * 60)

