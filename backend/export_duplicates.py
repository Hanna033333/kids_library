import os
import sys
import csv
from collections import defaultdict

# Add current directory to path
sys.path.append(os.getcwd())

from core.database import supabase

def export_duplicates_to_csv():
    print("데이터 가져오는 중...")
    
    all_books = []
    page = 0
    limit = 1000
    
    # 1. Fetch all data
    while True:
        start = page * limit
        end = start + limit - 1
        
        response = supabase.table("childbook_items") \
            .select("id, title, author, publisher, pangyo_callno, isbn") \
            .range(start, end) \
            .execute()
            
        if not response.data:
            break
            
        all_books.extend(response.data)
        
        if len(response.data) < limit:
            break
            
        page += 1
        print(f"{len(all_books)}권 데이터 로드 완료")

    print(f"총 {len(all_books)}권 분석 시작...")

    # 2. Group by call number
    call_groups = defaultdict(list)
    for book in all_books:
        callno = book.get("pangyo_callno")
        # Ignore empty or "없음" call numbers
        if not callno or callno == "없음":
            continue
        call_groups[callno].append(book)

    # 3. Filter duplicates (count > 1)
    duplicates = []
    for callno, books in call_groups.items():
        if len(books) > 1:
            for book in books:
                duplicates.append(book)

    # Sort by call number
    duplicates.sort(key=lambda x: x['pangyo_callno'])

    output_file = "check_duplicates_cleaned.csv"
    
    # 4. Write to CSV
    print(f"중복된 책 {len(duplicates)}권을 {output_file}로 저장합니다... (청구기호 '없음' 제외)")
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # Header
        writer.writerow(['ID', '청구기호', '제목', '저자', '출판사', 'ISBN', '비고(수정할청구기호)'])
        
        for book in duplicates:
            writer.writerow([
                book['id'],
                book['pangyo_callno'],
                book['title'],
                book['author'],
                book['publisher'],
                book['isbn'],
                '' # Empty column for user to fill in
            ])

    print("완료!")

if __name__ == "__main__":
    try:
        export_duplicates_to_csv()
    except Exception as e:
        print(f"오류 발생: {e}")
