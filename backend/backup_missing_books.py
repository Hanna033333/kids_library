import os
import sys
import csv
from datetime import datetime

# Add current directory to path to allow imports
sys.path.append(os.getcwd())

from core.database import supabase

def backup_missing_books():
    print("청구기호 '없음' 데이터 백업 시작...")
    
    # Fetch all books with '없음' call number
    # Using a large limit or pagination. Since it's ~2500, we can try fetching in one go or pages.
    # Supabase max yield is usually 1000 without range.
    
    all_books = []
    page = 0
    limit = 1000
    
    while True:
        start = page * limit
        end = start + limit - 1
        
        response = supabase.table("childbook_items") \
            .select("*") \
            .eq("pangyo_callno", "없음") \
            .range(start, end) \
            .execute()
            
        data = response.data
        if not data:
            break
            
        all_books.extend(data)
        print(f"{len(all_books)}권 로드됨...")
        
        if len(data) < limit:
            break
            
        page += 1
        
    print(f"총 {len(all_books)}권의 '청구기호 없음' 도서를 찾았습니다.")
    
    filename = f"missing_books_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(os.getcwd(), filename)
    
    if all_books:
        keys = all_books[0].keys()
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_books)
            
        print(f"백업 완료: {filepath}")
    else:
        print("백업할 데이터가 없습니다.")

if __name__ == "__main__":
    try:
        backup_missing_books()
    except Exception as e:
        print(f"오류 발생: {e}")
