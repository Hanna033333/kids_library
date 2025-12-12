"""
ISBN과 pangyo_callno 둘 다 없는 남은 항목을 CSV로 추출
"""
from supabase_client import supabase
import csv

print("=" * 60)
print("남은 항목 CSV 추출")
print("=" * 60)
print()

# ISBN과 pangyo_callno 둘 다 없는 항목 조회
child_items = []
page = 0
page_size = 1000

print("데이터 조회 중...")
while True:
    res = supabase.table("childbook_items").select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
    if not res.data:
        break
    
    for item in res.data:
        isbn = item.get("isbn")
        pangyo_callno = item.get("pangyo_callno")
        
        has_isbn = isbn and len(str(isbn).strip()) > 0
        has_pangyo_callno = pangyo_callno and len(str(pangyo_callno).strip()) > 0
        
        if not has_isbn and not has_pangyo_callno:
            child_items.append(item)
    
    if len(res.data) < page_size:
        break
    page += 1

print(f"조회 완료: {len(child_items)}개 항목")
print()

# CSV 파일로 저장
csv_filename = "remaining_items_no_isbn_no_callno.csv"
print(f"CSV 파일로 저장 중: {csv_filename}")

# CSV 헤더 정의
fieldnames = ['id', 'title', 'author', 'publisher', 'publication_year', 'isbn', 'pangyo_callno', 'description']

with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for item in child_items:
        row = {
            'id': item.get('id', ''),
            'title': item.get('title', ''),
            'author': item.get('author', ''),
            'publisher': item.get('publisher', ''),
            'publication_year': item.get('publication_year', ''),
            'isbn': item.get('isbn', ''),
            'pangyo_callno': item.get('pangyo_callno', ''),
            'description': item.get('description', '')
        }
        writer.writerow(row)

print(f"✅ 저장 완료: {csv_filename}")
print(f"   총 {len(child_items)}개 항목")
print()
print("=" * 60)

