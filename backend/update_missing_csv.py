import csv
import os
from core.database import supabase

def update_csv_with_callnos():
    input_file = "missing_books_export.csv"
    output_file = "missing_books_export_v3.csv"
    
    if not os.path.exists(input_file):
        print(f"오류: {input_file} 파일이 존재하지 않습니다.")
        return

    print(f"'{input_file}' 파일을 읽어 청구기호 정보를 추가합니다...")
    
    fieldnames = ['isbn', 'childbook_pangyo_callno', 'library_pangyo_callno', 'title', 'author', 'publisher']
    missing_books = []
    
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        total = len(rows)
        print(f"총 {total}권의 도서 정보를 처리합니다.")
        
        for i, row in enumerate(rows):
            isbn = row.get('isbn')
            if (i + 1) % 50 == 0:
                print(f"진행 상황: {i + 1}/{total} 도서 처리 중...")
            
            # 1. childbook_items에서 pangyo_callno 가져오기
            # (기존 CSV의 pangyo_callno가 childbook_items의 것임)
            child_callno = row.get('pangyo_callno', '')
            
            # 2. library_items에서 pangyo_callno 가져오기
            lib_callno = ''
            if isbn:
                lib_resp = supabase.table("library_items")\
                    .select("pangyo_callno")\
                    .eq("isbn", isbn)\
                    .execute()
                
                if lib_resp.data:
                    lib_callno = ", ".join([item['pangyo_callno'] for item in lib_resp.data if item.get('pangyo_callno')])
            
            new_row = {
                'isbn': isbn,
                'childbook_pangyo_callno': child_callno,
                'library_pangyo_callno': lib_callno,
                'title': row.get('title', ''),
                'author': row.get('author', ''),
                'publisher': row.get('publisher', '')
            }
            missing_books.append(new_row)
            
        # CSV 저장
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(missing_books)
            
        print(f"성공적으로 '{output_file}' 파일에 저장되었습니다.")
        print(f"파일 경로: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"작업 중 오류 발생: {e}")

if __name__ == "__main__":
    update_csv_with_callnos()
