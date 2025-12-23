import asyncio
import csv
import os
from typing import List, Dict
from core.database import supabase
from services.loan_status import fetch_loan_status_batch

async def export_missing_books():
    print("소장되지 않은 도서(미소장) 추출을 시작합니다...")
    
    # 1. DB에서 모든 도서 정보 가져오기
    all_books = []
    page_size = 1000
    offset = 0
    
    while True:
        print(f"데이터베이스에서 도서 정보를 불러오는 중... (오프셋: {offset})")
        # childbook_items에서 기본 정보 가져오기
        response = supabase.table("childbook_items")\
            .select("id, isbn, pangyo_callno, title, author, publisher")\
            .range(offset, offset + page_size - 1)\
            .execute()
        
        batch = response.data
        if not batch:
            break
            
        all_books.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
        
    print(f"총 {len(all_books)}권의 도서 정보를 불러왔습니다.")
    
    # 2. 대출 상태 확인 (병렬 처리)
    missing_books = []
    batch_size = 50
    
    print(f"대출 가능 여부 확인 중 (배치 크기: {batch_size})...")
    
    for i in range(0, len(all_books), batch_size):
        current_batch = all_books[i:i + batch_size]
        print(f"진행 상황: {i}/{len(all_books)} 도서 확인 중...")
        
        loan_statuses = await fetch_loan_status_batch(current_batch)
        
        for book in current_batch:
            book_id = book['id']
            status_info = loan_statuses.get(book_id)
            
            if status_info and status_info.get('status') == '미소장':
                # 미소장인 경우에만 library_items에서 pangyo_callno 조회 (효율적)
                isbn = book.get('isbn')
                if isbn:
                    lib_resp = supabase.table("library_items")\
                        .select("pangyo_callno")\
                        .eq("isbn", isbn)\
                        .execute()
                    
                    if lib_resp.data:
                        book['lib_pangyo_callno'] = ", ".join([item['pangyo_callno'] for item in lib_resp.data if item.get('pangyo_callno')])
                    else:
                        book['lib_pangyo_callno'] = ''
                else:
                    book['lib_pangyo_callno'] = ''
                    
                missing_books.append(book)
    
    print(f"확인 완료. 미소장 도서 총 {len(missing_books)}권을 찾았습니다.")
    
    # 3. CSV 파일로 저장
    output_file = "missing_books_export_v2.csv"
    fieldnames = ['isbn', 'childbook_pangyo_callno', 'library_pangyo_callno', 'title', 'author', 'publisher']
    
    try:
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for book in missing_books:
                row = {
                    'isbn': book.get('isbn', ''),
                    'childbook_pangyo_callno': book.get('pangyo_callno', ''),
                    'library_pangyo_callno': book.get('lib_pangyo_callno', ''),
                    'title': book.get('title', ''),
                    'author': book.get('author', ''),
                    'publisher': book.get('publisher', '')
                }
                writer.writerow(row)
        
        print(f"성공적으로 '{output_file}' 파일에 저장되었습니다.")
        print(f"파일 경로: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"CSV 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(export_missing_books())
