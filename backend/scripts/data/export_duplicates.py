import csv
from supabase_client import supabase
from collections import defaultdict

def export_duplicates_to_csv():
    # 1. library_items에서 ISBN별 청구기호 맵핑 생성
    print("📚 library_items 조회 중 (전체 데이터)...")
    isbn_to_lib_callno = {}
    
    # 36,000개가 넘는 데이터를 페이지네이션으로 가져옴
    batch_size = 1000
    offset = 0
    while True:
        lib_response = supabase.table("library_items") \
            .select("isbn, pangyo_callno") \
            .range(offset, offset + batch_size - 1) \
            .execute()
        
        if not lib_response.data:
            break
            
        for item in lib_response.data:
            isbn = item.get("isbn")
            lib_callno = item.get("pangyo_callno")
            if isbn and lib_callno:
                # ISBN에서 하이픈이나 공백 제거하여 매칭 확률 높임
                clean_isbn = "".join(filter(str.isdigit, str(isbn)))
                if clean_isbn:
                    isbn_to_lib_callno[clean_isbn] = lib_callno
        
        offset += batch_size
        if len(lib_response.data) < batch_size:
            break
            
    print(f"✅ 총 {len(isbn_to_lib_callno)}개의 Library ISBN 매핑 완료")

    # 2. childbook_items에서 중복 청구기호 찾기
    print("🔍 childbook_items 조회 중...")
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
    
    # 3. CSV 작성
    filename = "duplicates_for_manual_check.csv"
    try:
        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["청구기호", "Library 청구기호", "제목", "ISBN", "권차(입력필요)", "DB_ID", "이미지URL"])
            
            for callno, books in duplicates.items():
                for book in books:
                    isbn = book.get("isbn") or ""
                    # 매칭을 위해 ISBN 클리닝
                    clean_isbn = "".join(filter(str.isdigit, str(isbn)))
                    
                    # Excel에서 큰 숫자가 지수로 표시되는 것을 방지하기 위해 형식을 지정합니다.
                    formatted_isbn = f"\t{isbn}" if isbn else ""
                    
                    lib_callno = isbn_to_lib_callno.get(clean_isbn, "")
                    writer.writerow([
                        callno,
                        lib_callno,
                        book.get("title"),
                        formatted_isbn,
                        "", # 권차 입력란
                        book.get("id"),
                        book.get("saved_image_url") or ""
                    ])
                    
        print(f"✅ {filename} 파일이 생성되었습니다.")
        print(f"총 {sum(len(b) for b in duplicates.values())}권의 책이 포함되어 있습니다.")
    except PermissionError:
        print(f"❌ 오류: {filename} 파일이 열려 있어서 작성할 수 없습니다. 파일을 닫고 다시 시도해주세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    export_duplicates_to_csv()
