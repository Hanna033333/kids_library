"""
mismatched_isbn_books.csv 파일을 읽어서
library_items의 청구기호(callno)를 childbook_items의 pangyo_callno에 업데이트
"""
from supabase_client import supabase
import csv
import sys

print("=" * 60)
print("CSV 파일에서 pangyo_callno 업데이트")
print("=" * 60)
print()

# 1) CSV 파일 읽기
csv_filename = "mismatched_isbn_books.csv"
print(f"1. CSV 파일 읽기: {csv_filename}")

items_to_update = []
try:
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            child_id = row.get('child_id', '').strip()
            lib_callno = row.get('lib_callno', '').strip()
            
            if child_id and lib_callno:
                items_to_update.append({
                    'child_id': int(child_id),
                    'lib_callno': lib_callno
                })
    
    print(f"   [OK] {len(items_to_update):,}개 항목 로드됨")
except Exception as e:
    print(f"   [ERROR] 오류: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if len(items_to_update) == 0:
    print("   [WARN] 업데이트할 항목이 없습니다.")
    sys.exit(0)

print()

# 2) pangyo_callno 업데이트
print("2. pangyo_callno 업데이트 중...")
print()

success_count = 0
fail_count = 0

for idx, item in enumerate(items_to_update):
    child_id = item['child_id']
    lib_callno = item['lib_callno']
    
    try:
        supabase.table("childbook_items").update({
            "pangyo_callno": lib_callno
        }).eq("id", child_id).execute()
        success_count += 1
    except Exception as e:
        fail_count += 1
        if fail_count <= 10:
            print(f"   [ERROR] ID {child_id} 업데이트 실패: {e}")
    
    # 진행 상황 출력 (50개마다)
    if (idx + 1) % 50 == 0:
        print(f"   진행 중: {idx + 1}/{len(items_to_update)} (성공: {success_count}, 실패: {fail_count})")
        sys.stdout.flush()

print()
print("=" * 60)
print("[OK] 완료!")
print("-" * 60)
print(f"총 처리: {len(items_to_update):,}개")
print(f"성공: {success_count:,}개")
print(f"실패: {fail_count:,}개")
print("=" * 60)

