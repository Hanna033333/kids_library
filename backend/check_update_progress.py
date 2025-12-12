"""
CSV 파일 업데이트 진행 상황 확인
"""
from supabase_client import supabase
import csv

print("=" * 60)
print("CSV 파일 업데이트 진행 상황 확인")
print("=" * 60)
print()

# CSV 파일에서 child_id 목록 읽기
csv_filename = "mismatched_isbn_books.csv"
child_ids_from_csv = set()

try:
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            child_id = row.get('child_id', '').strip()
            if child_id:
                child_ids_from_csv.add(int(child_id))
    
    print(f"CSV 파일의 항목 수: {len(child_ids_from_csv):,}개")
except Exception as e:
    print(f"CSV 파일 읽기 오류: {e}")
    exit(1)

print()

# 각 child_id에 대해 pangyo_callno 확인
print("업데이트 상태 확인 중...")
updated_count = 0
not_updated_count = 0

# 배치로 확인 (100개씩)
child_ids_list = list(child_ids_from_csv)
batch_size = 100

for i in range(0, len(child_ids_list), batch_size):
    batch_ids = child_ids_list[i:i+batch_size]
    
    # Supabase에서 배치 조회
    ids_str = ','.join(map(str, batch_ids))
    res = supabase.table("childbook_items").select("id,pangyo_callno").in_("id", batch_ids).execute()
    
    for item in res.data:
        child_id = item.get("id")
        pangyo_callno = item.get("pangyo_callno")
        
        if pangyo_callno and len(str(pangyo_callno).strip()) > 0:
            updated_count += 1
        else:
            not_updated_count += 1
    
    # 진행 상황 출력
    processed = min(i + batch_size, len(child_ids_list))
    print(f"   확인 중: {processed}/{len(child_ids_list)} (업데이트됨: {updated_count}, 미업데이트: {not_updated_count})")

print()
print("=" * 60)
print("결과")
print("=" * 60)
print(f"CSV 파일 항목 수: {len(child_ids_from_csv):,}개")
print(f"업데이트 완료: {updated_count:,}개 ({updated_count/len(child_ids_from_csv)*100:.1f}%)")
print(f"미업데이트: {not_updated_count:,}개 ({not_updated_count/len(child_ids_from_csv)*100:.1f}%)")
print("=" * 60)

