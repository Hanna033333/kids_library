"""
CSV 파일의 항목 중 실제로 새로 업데이트된 항목 확인
"""
from supabase_client import supabase
import csv

print("=" * 60)
print("새로 업데이트된 항목 확인")
print("=" * 60)
print()

# CSV 파일 읽기
csv_filename = "mismatched_isbn_books.csv"
csv_items = []

with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        child_id = row.get('child_id', '').strip()
        lib_callno = row.get('lib_callno', '').strip()
        if child_id and lib_callno:
            csv_items.append({
                'child_id': int(child_id),
                'expected_callno': lib_callno
            })

print(f"CSV 파일 항목 수: {len(csv_items):,}개")
print()

# Supabase에서 실제 값 확인
print("Supabase에서 확인 중...")
matched_count = 0
newly_updated_count = 0  # CSV의 callno와 일치하는 항목

batch_size = 100
for i in range(0, len(csv_items), batch_size):
    batch = csv_items[i:i+batch_size]
    batch_ids = [item['child_id'] for item in batch]
    
    res = supabase.table("childbook_items").select("id,pangyo_callno").in_("id", batch_ids).execute()
    db_items = {item['id']: item.get('pangyo_callno', '') for item in res.data}
    
    for csv_item in batch:
        child_id = csv_item['child_id']
        expected_callno = csv_item['expected_callno']
        actual_callno = db_items.get(child_id, '')
        
        if actual_callno and str(actual_callno).strip() == str(expected_callno).strip():
            matched_count += 1
            newly_updated_count += 1

print()
print("=" * 60)
print("결과")
print("=" * 60)
print(f"CSV 항목 수: {len(csv_items):,}개")
print(f"✅ CSV의 callno와 일치 (업데이트됨): {matched_count:,}개")
print("=" * 60)

