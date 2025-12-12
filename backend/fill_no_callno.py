"""
library_items에 ISBN이 없는 책들(소장되지 않은 책)의 pangyo_callno에 '없음' 채우기
"""
from supabase_client import supabase

print("=" * 60)
print("소장되지 않은 책에 '없음' 채우기")
print("=" * 60)
print()

# 1) pangyo_callno가 없는 childbook_items 조회
print("1. pangyo_callno가 없는 항목 조회 중...")
child_items_no_callno = []
page = 0
page_size = 1000

while True:
    res = supabase.table("childbook_items").select("id,isbn,pangyo_callno").range(page * page_size, (page + 1) * page_size - 1).execute()
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
            isbn_normalized = ''.join(filter(str.isdigit, str(isbn13)))
            if len(isbn_normalized) == 13:
                library_isbn_set.add(isbn_normalized)
    
    if len(res.data) < page_size:
        break
    page += 1

print(f"   [OK] library_items ISBN-13: {len(library_isbn_set):,}개")
print()

# 3) library_items에 ISBN이 없는 항목 찾아서 '없음' 채우기
print("3. 소장되지 않은 책에 '없음' 채우기...")
print()

success_count = 0
skip_count = 0  # ISBN이 없거나 형식 오류인 경우

for idx, child_item in enumerate(child_items_no_callno):
    child_id = child_item.get("id")
    child_isbn = child_item.get("isbn")
    
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
    
    # library_items에 ISBN이 없는 경우 '없음' 채우기
    if child_isbn_normalized and len(child_isbn_normalized) == 13:
        if child_isbn_normalized not in library_isbn_set:
            try:
                supabase.table("childbook_items").update({
                    "pangyo_callno": "없음"
                }).eq("id", child_id).execute()
                success_count += 1
            except Exception as e:
                if success_count < 5:
                    print(f"   [ERROR] ID {child_id} 업데이트 실패: {e}")
        else:
            # library_items에 ISBN이 있는 경우는 건너뜀 (이미 처리되었거나 다른 이유로 없음)
            skip_count += 1
    else:
        # ISBN이 없거나 형식 오류인 경우는 건너뜀
        skip_count += 1
    
    # 진행 상황 출력 (500개마다)
    if (idx + 1) % 500 == 0:
        print(f"   진행 중: {idx + 1}/{len(child_items_no_callno)} (성공: {success_count}, 건너뜀: {skip_count})")

print()
print("=" * 60)
print("[OK] 완료!")
print("-" * 60)
print(f"총 처리: {len(child_items_no_callno):,}개")
print(f"'없음' 채움: {success_count:,}개")
print(f"건너뜀: {skip_count:,}개")
print("=" * 60)

