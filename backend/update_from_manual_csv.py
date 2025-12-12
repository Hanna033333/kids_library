"""
수동 입력된 CSV 파일을 읽어서 pangyo_callno 업데이트
"""
from supabase_client import supabase
import csv

print("=" * 60)
print("수동 입력 CSV에서 pangyo_callno 업데이트")
print("=" * 60)
print()

csv_filename = "no_callno_items_manual.csv"

print(f"CSV 파일 읽기: {csv_filename}")

items_to_update = []
try:
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            child_id = row.get('id', '').strip()
            manual_callno = row.get('pangyo_callno_manual', '').strip()
            
            if child_id and manual_callno and len(manual_callno) > 0:
                items_to_update.append({
                    'child_id': int(child_id),
                    'pangyo_callno': manual_callno
                })
    
    print(f"업데이트할 항목: {len(items_to_update):,}개")
except Exception as e:
    print(f"오류: {e}")
    exit(1)

if len(items_to_update) == 0:
    print("업데이트할 항목이 없습니다.")
    exit(0)

print()
print("Supabase 업데이트 중...")

success_count = 0
fail_count = 0

for idx, item in enumerate(items_to_update):
    child_id = item['child_id']
    callno = item['pangyo_callno']
    
    try:
        supabase.table("childbook_items").update({
            "pangyo_callno": callno
        }).eq("id", child_id).execute()
        success_count += 1
    except Exception as e:
        fail_count += 1
        if fail_count <= 5:
            print(f"  [ERROR] ID {child_id} 업데이트 실패: {e}")
    
    if (idx + 1) % 100 == 0:
        print(f"  진행 중: {idx + 1}/{len(items_to_update)}")

print()
print("=" * 60)
print("[OK] 완료!")
print("-" * 60)
print(f"총 처리: {len(items_to_update):,}개")
print(f"성공: {success_count:,}개")
print(f"실패: {fail_count:,}개")
print("=" * 60)

