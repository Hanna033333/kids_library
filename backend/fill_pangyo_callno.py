"""
childbook_items에서 pangyo_callno가 없는 항목에 대해 library_items와 매칭하여 채우기
"""
from supabase_client import supabase
import time
import sys

print("=" * 60)
print("pangyo_callno 채우기")
print("=" * 60)
print()

# 1) pangyo_callno가 없는 항목 조회
print("1. pangyo_callno가 없는 항목 조회 중...")
try:
    child_items = []
    page = 0
    page_size = 1000
    
    while True:
        res = supabase.table("childbook_items").select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
        if not res.data:
            break
        
        for item in res.data:
            pangyo_callno = item.get("pangyo_callno")
            has_pangyo_callno = pangyo_callno and len(str(pangyo_callno).strip()) > 0
            
            if not has_pangyo_callno:
                child_items.append(item)
        
        if len(res.data) < page_size:
            break
        page += 1
    
    print(f"   [OK] pangyo_callno가 없는 항목: {len(child_items):,}개")
except Exception as e:
    print(f"   [ERROR] 오류: {e}")
    sys.exit(1)

if len(child_items) == 0:
    print("\n[OK] 모든 항목에 pangyo_callno가 이미 있습니다!")
    sys.exit(0)

print()

# 2) library_items에서 모든 데이터 가져오기 (ISBN 또는 제목으로 매칭)
print("2. library_items 데이터 로드 중...")
try:
    library_items = []
    page = 0
    page_size = 1000
    
    while True:
        res = supabase.table("library_items").select("isbn13,callno,title").range(page * page_size, (page + 1) * page_size - 1).execute()
        if not res.data:
            break
        
        library_items.extend(res.data)
        
        if len(res.data) < page_size:
            break
        page += 1
    
    print(f"   [OK] library_items: {len(library_items):,}개 로드됨")
except Exception as e:
    print(f"   [ERROR] 오류: {e}")
    sys.exit(1)

print()

# 3) ISBN 또는 제목으로 매칭
print("3. ISBN 또는 제목으로 매칭 중...")
print()

success_count = 0
fail_count = 0
isbn_match_count = 0
title_match_count = 0

# ISBN으로 매칭할 수 있는 항목 먼저 처리
for idx, child_item in enumerate(child_items):
    child_id = child_item.get("id")
    child_isbn = child_item.get("isbn")
    child_title = child_item.get("title", "").strip()
    
    matched_callno = None
    
    # ISBN으로 매칭 시도
    if child_isbn and len(str(child_isbn).strip()) > 0:
        # childbook_items의 ISBN 정규화 (숫자만 추출)
        child_isbn_normalized = ''.join(filter(str.isdigit, str(child_isbn)))
        
        for lib_item in library_items:
            lib_isbn13 = lib_item.get("isbn13")
            if lib_isbn13:
                # library_items의 ISBN-13 정규화
                lib_isbn_normalized = ''.join(filter(str.isdigit, str(lib_isbn13)))
                
                # ISBN-13 매칭 (13자리)
                if len(child_isbn_normalized) == 13 and child_isbn_normalized == lib_isbn_normalized:
                    matched_callno = lib_item.get("callno")
                    if matched_callno and len(str(matched_callno).strip()) > 0:
                        isbn_match_count += 1
                        break
                # ISBN-10을 ISBN-13으로 변환하여 매칭 시도
                elif len(child_isbn_normalized) == 10 and len(lib_isbn_normalized) == 13:
                    # ISBN-10을 ISBN-13으로 변환 (978 + ISBN-10 앞 9자리 + 체크섬)
                    isbn13_from_10 = "978" + child_isbn_normalized[:9]
                    checksum = sum(int(digit) * (3 if i % 2 == 1 else 1) for i, digit in enumerate(isbn13_from_10[:12])) % 10
                    checksum = (10 - checksum) % 10
                    isbn13_from_10 = isbn13_from_10[:12] + str(checksum)
                    
                    if isbn13_from_10 == lib_isbn_normalized:
                        matched_callno = lib_item.get("callno")
                        if matched_callno and len(str(matched_callno).strip()) > 0:
                            isbn_match_count += 1
                            break
    
    # ISBN 매칭 실패 시 제목으로 매칭 시도
    if not matched_callno and child_title:
        # 정확한 제목 매칭
        for lib_item in library_items:
            lib_title = lib_item.get("title", "").strip()
            if lib_title and lib_title == child_title:
                matched_callno = lib_item.get("callno")
                if matched_callno and len(str(matched_callno).strip()) > 0:
                    title_match_count += 1
                    break
    
    # 매칭된 경우 업데이트
    if matched_callno:
        try:
            supabase.table("childbook_items").update({
                "pangyo_callno": matched_callno
            }).eq("id", child_id).execute()
            success_count += 1
        except Exception as e:
            print(f"   [ERROR] ID {child_id} 업데이트 실패: {e}")
            fail_count += 1
    else:
        fail_count += 1
    
    # 진행 상황 출력 (100개마다)
    if (idx + 1) % 100 == 0:
        print(f"   진행 중: {idx + 1}/{len(child_items)} (성공: {success_count}, 실패: {fail_count})")
        print(f"            ISBN 매칭: {isbn_match_count}개, 제목 매칭: {title_match_count}개")

print()
print("=" * 60)
print("[OK] 완료!")
print("-" * 60)
print(f"총 처리: {len(child_items):,}개")
print(f"성공: {success_count:,}개")
print(f"  - ISBN 매칭: {isbn_match_count:,}개")
print(f"  - 제목 매칭: {title_match_count:,}개")
print(f"실패: {fail_count:,}개")
print("=" * 60)

