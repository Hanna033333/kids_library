"""
mismatched_isbn_books.csv에 있는 항목들에 대해 pangyo_callno 채우기
ISBN이 같으므로 library_items의 callno를 사용
"""
from supabase_client import supabase
import csv

print("=" * 60)
print("ISBN이 같은 항목들에 pangyo_callno 채우기")
print("=" * 60)
print()

# 1) CSV 파일 읽기
csv_filename = "mismatched_isbn_books.csv"
print(f"1. CSV 파일 읽기: {csv_filename}")

mismatched_items = []
try:
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            mismatched_items.append({
                'child_id': row.get('child_id'),
                'child_isbn': row.get('child_isbn'),
                'lib_callno': row.get('lib_callno')
            })
    print(f"   [OK] {len(mismatched_items):,}개 항목 로드됨")
except Exception as e:
    print(f"   [ERROR] 오류: {e}")
    exit(1)

print()

# 2) pangyo_callno 업데이트
print("2. pangyo_callno 업데이트 중...")
print()

success_count = 0
fail_count = 0
skip_count = 0

for idx, item in enumerate(mismatched_items):
    child_id = item.get('child_id')
    lib_callno = item.get('lib_callno')
    
    if not child_id:
        skip_count += 1
        continue
    
    if not lib_callno or len(str(lib_callno).strip()) == 0:
        skip_count += 1
        continue
    
    try:
        supabase.table("childbook_items").update({
            "pangyo_callno": lib_callno.strip()
        }).eq("id", int(child_id)).execute()
        success_count += 1
    except Exception as e:
        fail_count += 1
        if fail_count <= 5:
            print(f"   [ERROR] ID {child_id} 업데이트 실패: {e}")
    
    # 진행 상황 출력 (100개마다)
    if (idx + 1) % 100 == 0:
        print(f"   진행 중: {idx + 1}/{len(mismatched_items)} (성공: {success_count}, 실패: {fail_count}, 건너뜀: {skip_count})")

print()
print("=" * 60)
print("[OK] 완료!")
print("-" * 60)
print(f"총 처리: {len(mismatched_items):,}개")
print(f"성공: {success_count:,}개")
print(f"실패: {fail_count:,}개")
print(f"건너뜀: {skip_count:,}개")
print("=" * 60)

