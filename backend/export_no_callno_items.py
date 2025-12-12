"""
pangyo_callno가 '없음'인 항목들을 CSV로 추출
"""
from supabase_client import supabase
import csv

print("=" * 60)
print("pangyo_callno가 '없음'인 항목 CSV 추출")
print("=" * 60)
print()

# pangyo_callno가 '없음'인 항목 조회
print("데이터 조회 중...")
items_no_callno = []
page = 0
page_size = 1000

while True:
    res = supabase.table("childbook_items").select("id,isbn,title,author,publisher,pangyo_callno").eq("pangyo_callno", "없음").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
    items_no_callno.extend(res.data)
    
    if len(res.data) < page_size:
        break
    page += 1

print(f"조회 완료: {len(items_no_callno):,}개 항목")
print()

# CSV 파일로 저장
csv_filename = "no_callno_items.csv"
print(f"CSV 파일로 저장 중: {csv_filename}")

fieldnames = ['id', 'isbn', 'title', 'author', 'publisher', 'pangyo_callno']

with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for item in items_no_callno:
        row = {
            'id': item.get('id', ''),
            'isbn': item.get('isbn', ''),
            'title': item.get('title', ''),
            'author': item.get('author', ''),
            'publisher': item.get('publisher', ''),
            'pangyo_callno': item.get('pangyo_callno', '')
        }
        writer.writerow(row)

print(f"✅ 저장 완료: {csv_filename}")
print(f"   총 {len(items_no_callno):,}개 항목")
print()
print("=" * 60)

