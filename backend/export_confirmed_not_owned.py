"""미소장 확정 도서 목록 추출"""
import csv
from core.database import supabase

# 1. 여전히 미소장인 11권 (ISBN 업데이트했지만 미소장)
still_not_owned_ids = []
with open('updated_books_loan_status.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['status'] == '미소장':
            still_not_owned_ids.append(int(row['id']))

print(f"여전히 미소장: {len(still_not_owned_ids)}권")

# 2. ISBN 업데이트 안 된 책들 (동일하거나 못 찾음)
not_updated_ids = []
with open('not_owned_isbn_update.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['updated'] != 'True':
            not_updated_ids.append(int(row['id']))

print(f"ISBN 업데이트 안 됨: {len(not_updated_ids)}권")

# 합치기
all_ids = list(set(still_not_owned_ids + not_updated_ids))
print(f"총 미소장 확정: {len(all_ids)}권")

# DB에서 조회
response = supabase.table("childbook_items")\
    .select("id, title, isbn, author, publisher, pangyo_callno")\
    .in_("id", all_ids)\
    .execute()

books = response.data

# CSV 저장
output_file = 'confirmed_not_owned_books.csv'
with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'isbn', 'author', 'publisher', 'pangyo_callno'])
    writer.writeheader()
    
    for book in books:
        writer.writerow({
            'title': book.get('title', ''),
            'isbn': book.get('isbn', ''),
            'author': book.get('author', ''),
            'publisher': book.get('publisher', ''),
            'pangyo_callno': book.get('pangyo_callno', '')
        })

print(f"\n✅ CSV 저장 완료: {output_file}")
print(f"📊 총 {len(books)}권의 미소장 확정 도서")
