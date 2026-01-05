from supabase_client import supabase

def update_new_callnos():
    """원래 청구기호 없던 책에 웹 스크래핑 데이터 추가"""
    print("📚 원래 청구기호 없던 책 업데이트 중...\n")
    
    # 원래 청구기호 없고, 웹 스크래핑은 있는 책
    res = supabase.table("childbook_items") \
        .select("id, title, web_scraped_callno") \
        .is_("pangyo_callno", "null") \
        .not_.is_("web_scraped_callno", "null") \
        .neq("web_scraped_callno", "NotFound") \
        .execute()
    
    books = res.data
    
    print(f"업데이트 대상: {len(books)}권\n")
    
    updated = 0
    for book in books:
        book_id = book['id']
        scraped = book['web_scraped_callno']
        
        supabase.table("childbook_items") \
            .update({"pangyo_callno": scraped}) \
            .eq("id", book_id) \
            .execute()
        
        updated += 1
        print(f"✅ {book['title']}")
        print(f"   청구기호: {scraped}\n")
    
    print(f"\n✅ 업데이트 완료: {updated}권")

if __name__ == "__main__":
    update_new_callnos()
