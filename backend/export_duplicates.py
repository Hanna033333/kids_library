import csv
from supabase_client import supabase
from collections import defaultdict

def export_duplicates_to_csv():
    # 1. 중복 청구기호 찾기
    response = supabase.table("childbook_items").select("*").execute()
    books = response.data
    
    callno_groups = defaultdict(list)
    for book in books:
        callno = book.get("pangyo_callno")
        if callno and callno.strip():
            callno_groups[callno].append(book)
            
    duplicates = {
        callno: books 
        for callno, books in callno_groups.items() 
        if len(books) > 1
    }
    
    # 2. CSV 작성
    filename = "duplicates_for_manual_check.csv"
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["청구기호", "제목", "ISBN", "권차(입력필요)", "DB_ID", "이미지URL"])
        
        for callno, books in duplicates.items():
            for book in books:
                writer.writerow([
                    callno,
                    book.get("title"),
                    book.get("isbn"),
                    "", # 권차 입력란
                    book.get("id"),
                    book.get("saved_image_url") or ""
                ])
                
    print(f"✅ {filename} 파일이 생성되었습니다.")
    print(f"총 {sum(len(b) for b in duplicates.values())}권의 책이 포함되어 있습니다.")

if __name__ == "__main__":
    export_duplicates_to_csv()
