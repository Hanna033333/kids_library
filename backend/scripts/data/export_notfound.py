import csv
from datetime import datetime
from supabase_client import supabase

def export_notfound():
    """NotFound 책들 CSV로 내보내기"""
    print("📄 NotFound 책 목록 추출 중...\n")
    
    # NotFound 책들 조회
    res = supabase.table("childbook_items") \
        .select("id, title, author, publisher, isbn, category, age") \
        .eq("web_scraped_callno", "NotFound") \
        .execute()
    
    books = res.data
    
    print(f"총 {len(books)}권 추출\n")
    
    # CSV 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"notfound_books_{timestamp}.csv"
    
    if books:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'author', 'publisher', 'isbn', 'category', 'age'])
            writer.writeheader()
            writer.writerows(books)
    
    print(f"✅ 저장 완료: {filename}")
    print(f"   판교도서관에 없는 책 {len(books)}권\n")

if __name__ == "__main__":
    export_notfound()
