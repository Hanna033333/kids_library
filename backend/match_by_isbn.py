"""
childbook_items와 library_items를 ISBN 기반으로 매칭하여
owned, pangyo_callno 필드를 업데이트
"""
from supabase_client import supabase
import sys

print("=" * 60)
print("childbook_items와 판교 도서관 매칭 (ISBN 기반)")
print("=" * 60)
print()

# 1) childbook_items 가져오기 (전체 데이터)
print("1. childbook_items 데이터 로딩 중...")
try:
    child_items = []
    page = 0
    page_size = 1000
    
    while True:
        res = supabase.table("childbook_items").select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
        if not res.data:
            break
        child_items.extend(res.data)
        if len(res.data) < page_size:
            break
        page += 1
    
    print(f"   ✅ {len(child_items):,}개 항목 로드 완료")
except Exception as e:
    print(f"   ❌ 오류: {e}")
    sys.exit(1)

print()

# 2) 판교 장서 가져오기 (전체 데이터)
print("2. library_items (판교 도서관) 데이터 로딩 중...")
try:
    pangyo_items = []
    page = 0
    page_size = 1000
    
    while True:
        res = supabase.table("library_items").select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
        if not res.data:
            break
        pangyo_items.extend(res.data)
        if len(res.data) < page_size:
            break
        page += 1
    
    print(f"   ✅ {len(pangyo_items):,}개 항목 로드 완료")
except Exception as e:
    print(f"   ❌ 오류: {e}")
    sys.exit(1)

print()

# 3) ISBN 기반 인덱스 생성
print("3. ISBN 기반 인덱스 생성 중...")
pangyo_by_isbn = {}
for item in pangyo_items:
    isbn13 = item.get("isbn13", "")
    if isbn13:
        # ISBN-13 정규화 (숫자만 추출)
        isbn_normalized = ''.join(filter(str.isdigit, str(isbn13)))
        if len(isbn_normalized) == 13:
            pangyo_by_isbn[isbn_normalized] = item

print(f"   ✅ {len(pangyo_by_isbn):,}개 ISBN 인덱스 생성 완료")
print()

# 4) childbook_items 루프 돌면서 ISBN으로 매칭
print("4. ISBN 기반 매칭 진행 중...")
print()

updates = []
matched_count = 0
unmatched_count = 0
no_isbn_count = 0

for idx, item in enumerate(child_items):
    # ISBN 필드 확인
    isbn = item.get("isbn")
    
    if not isbn or (isbn and len(str(isbn).strip()) == 0):
        updates.append({
            "id": item["id"],
            "owned": False,
            "similarity": 0,
            "pangyo_callno": None
        })
        no_isbn_count += 1
        unmatched_count += 1
        continue
    
    # ISBN 정규화 (숫자만 추출)
    isbn_normalized = ''.join(filter(str.isdigit, str(isbn)))
    
    # ISBN-13 형식 확인 (13자리)
    if len(isbn_normalized) == 13:
        # ISBN-10을 ISBN-13으로 변환 (필요한 경우)
        # ISBN-10은 978로 시작하는 ISBN-13으로 변환 가능
        if len(isbn_normalized) == 10:
            isbn_normalized = "978" + isbn_normalized[:9]
            # 체크섬 계산 (간단한 버전)
            checksum = sum(int(digit) * (3 if i % 2 == 1 else 1) for i, digit in enumerate(isbn_normalized[:12])) % 10
            checksum = (10 - checksum) % 10
            isbn_normalized = isbn_normalized[:12] + str(checksum)
    
    # 매칭 확인
    pangyo_book = pangyo_by_isbn.get(isbn_normalized)
    
    if pangyo_book:
        updates.append({
            "id": item["id"],
            "owned": True,
            "similarity": 100,  # ISBN 매칭은 100% 정확
            "pangyo_callno": pangyo_book.get("callno")
        })
        matched_count += 1
    else:
        updates.append({
            "id": item["id"],
            "owned": False,
            "similarity": 0,
            "pangyo_callno": None
        })
        unmatched_count += 1
    
    # 진행 상황 출력 (100개마다)
    if (idx + 1) % 100 == 0:
        print(f"   진행 중: {idx + 1}/{len(child_items)} ({matched_count}개 매칭됨)")

print()
print(f"   ✅ 매칭 완료!")
print(f"      - 매칭됨: {matched_count}개")
print(f"      - 매칭 안됨: {unmatched_count}개 (ISBN 없음: {no_isbn_count}개)")
print()

# 5) supabase 업데이트
print("5. Supabase 업데이트 중...")
print()

success_count = 0
error_count = 0

for idx, row in enumerate(updates):
    try:
        supabase.table("childbook_items").update({
            "owned": row["owned"],
            "similarity": row["similarity"],
            "pangyo_callno": row["pangyo_callno"]
        }).eq("id", row["id"]).execute()
        
        success_count += 1
        
        # 진행 상황 출력 (100개마다)
        if (idx + 1) % 100 == 0:
            print(f"   업데이트 중: {idx + 1}/{len(updates)}")
            
    except Exception as e:
        error_count += 1
        if error_count <= 5:  # 처음 5개 오류만 출력
            print(f"   ❌ ID {row['id']} 업데이트 오류: {e}")

print()
print("=" * 60)
print("✅ 완료!")
print("-" * 60)
print(f"총 처리: {len(updates)}개")
print(f"성공: {success_count}개")
if error_count > 0:
    print(f"실패: {error_count}개")
print(f"매칭됨: {matched_count}개")
print(f"매칭 안됨: {unmatched_count}개 (ISBN 없음: {no_isbn_count}개)")
print("=" * 60)

