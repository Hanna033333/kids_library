from supabase_client import supabase

def check_all_four():
    """4권 모두 다시 확인"""
    
    titles = ['눈의 여왕', '고릴라', '장갑', '로베르토']
    
    print("📚 상세 정보 재확인\n")
    
    for title in titles:
        res = supabase.table("childbook_items") \
            .select("id, title, isbn, author, publisher, pangyo_callno, web_scraped_callno") \
            .eq("title", title) \
            .execute()
        
        if res.data:
            for book in res.data:
                print(f"📖 [{book['id']}] {book['title']}")
                print(f"   ISBN: {book.get('isbn', 'N/A')}")
                print(f"   저자: {book.get('author', 'N/A')}")
                print(f"   출판사: {book.get('publisher', 'N/A')}")
                print(f"   pangyo_callno: {book.get('pangyo_callno', 'N/A')}")
                print(f"   web_scraped_callno: {book.get('web_scraped_callno', 'N/A')}")
                print()

if __name__ == "__main__":
    check_all_four()
