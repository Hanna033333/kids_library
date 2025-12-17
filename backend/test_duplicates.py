from supabase_client import supabase
from collections import defaultdict

# 모든 childbook_items 조회
response = supabase.table("childbook_items").select("id, isbn, title, pangyo_callno").execute()
books = response.data

# 청구기호별로 그룹화
callno_groups = defaultdict(list)
for book in books:
    callno = book.get("pangyo_callno")
    if callno and callno.strip():
        callno_groups[callno].append(book)

# 중복된 청구기호만 필터링
duplicates = {
    callno: books_list 
    for callno, books_list in callno_groups.items() 
    if len(books_list) > 1
}

print(f"Total duplicates: {len(duplicates)}")
print(f"Total books with duplicates: {sum(len(b) for b in duplicates.values())}")

# Top 10
sorted_dups = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
for callno, books_list in sorted_dups[:10]:
    print(f"\n{callno} - {len(books_list)} books")
    for book in books_list[:2]:
        print(f"  - {book.get('title', '')[:50]} [ISBN: {book.get('isbn', 'N/A')}]")
