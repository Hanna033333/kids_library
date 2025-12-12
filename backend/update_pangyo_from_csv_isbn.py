"""
mismatched_isbn_books.csv 파일의 child_id 리스트를 읽어서
각 항목의 ISBN으로 library_items에서 청구기호를 찾아
childbook_items의 pangyo_callno에 업데이트
"""
from supabase_client import supabase
import csv
import sys

print("=" * 60)
print("CSV 파일에서 ISBN으로 청구기호 찾아서 업데이트")
print("=" * 60)
print()

# 1) CSV 파일에서 child_id와 ISBN 읽기
csv_filename = "mismatched_isbn_books.csv"
print(f"1. CSV 파일 읽기: {csv_filename}")

child_ids = []
child_isbns = {}
try:
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            child_id = row.get('child_id', '').strip()
            child_isbn = row.get('child_isbn', '').strip()
            
            if child_id and child_isbn:
                child_id_int = int(child_id)
                child_ids.append(child_id_int)
                child_isbns[child_id_int] = child_isbn
    
    print(f"   [OK] {len(child_ids):,}개 항목 로드됨")
except Exception as e:
    print(f"   [ERROR] 오류: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if len(child_ids) == 0:
    print("   [WARN] 처리할 항목이 없습니다.")
    sys.exit(0)

print()

# 2) library_items에서 ISBN-13으로 인덱스 생성
print("2. library_items에서 청구기호 인덱스 생성 중...")
library_callno_by_isbn = {}
page = 0
page_size = 1000

while True:
    res = supabase.table("library_items").select("isbn13,callno").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
    for item in res.data:
        isbn13 = item.get("isbn13")
        callno = item.get("callno")
        
        if isbn13 and callno:
            # ISBN-13 정규화 (숫자만 추출)
            isbn_normalized = ''.join(filter(str.isdigit, str(isbn13)))
            if len(isbn_normalized) == 13:
                # 같은 ISBN이 여러 개 있을 수 있으므로 첫 번째 것만 저장
                if isbn_normalized not in library_callno_by_isbn:
                    library_callno_by_isbn[isbn_normalized] = callno
    
    if len(res.data) < page_size:
        break
    page += 1

print(f"   [OK] {len(library_callno_by_isbn):,}개 ISBN-13 인덱스 생성 완료")
print()

# 3) 각 child_id에 대해 청구기호 찾아서 업데이트
print("3. 청구기호 찾아서 업데이트 중...")
print()

success_count = 0
fail_count = 0
not_found_count = 0

for idx, child_id in enumerate(child_ids):
    child_isbn = child_isbns.get(child_id)
    if not child_isbn:
        fail_count += 1
        continue
    
    # ISBN 정규화
    child_isbn_normalized = ''.join(filter(str.isdigit, str(child_isbn)))
    
    # library_items에서 청구기호 찾기
    matched_callno = None
    
    if len(child_isbn_normalized) == 13:
        # ISBN-13 직접 매칭
        matched_callno = library_callno_by_isbn.get(child_isbn_normalized)
    elif len(child_isbn_normalized) == 10:
        # ISBN-10을 ISBN-13으로 변환하여 매칭 시도
        isbn13_from_10 = "978" + child_isbn_normalized[:9]
        checksum = sum(int(digit) * (3 if i % 2 == 1 else 1) for i, digit in enumerate(isbn13_from_10[:12])) % 10
        checksum = (10 - checksum) % 10
        isbn13_from_10 = isbn13_from_10[:12] + str(checksum)
        matched_callno = library_callno_by_isbn.get(isbn13_from_10)
    
    if matched_callno and len(str(matched_callno).strip()) > 0:
        try:
            supabase.table("childbook_items").update({
                "pangyo_callno": matched_callno.strip()
            }).eq("id", child_id).execute()
            success_count += 1
        except Exception as e:
            fail_count += 1
            if fail_count <= 10:
                print(f"   [ERROR] ID {child_id} 업데이트 실패: {e}")
    else:
        not_found_count += 1
    
    # 진행 상황 출력 (50개마다)
    if (idx + 1) % 50 == 0:
        print(f"   진행 중: {idx + 1}/{len(child_ids)} (성공: {success_count}, 실패: {fail_count}, 찾지못함: {not_found_count})")
        sys.stdout.flush()

print()
print("=" * 60)
print("[OK] 완료!")
print("-" * 60)
print(f"총 처리: {len(child_ids):,}개")
print(f"성공: {success_count:,}개")
print(f"실패: {fail_count:,}개")
print(f"청구기호 찾지 못함: {not_found_count:,}개")
print("=" * 60)

