from supabase_client import supabase

def check_new_callnos():
    """원래 청구기호 없었는데 웹 스크래핑으로 찾은 책들"""
    print("📊 원래 청구기호 없던 책 분석 중...\n")
    
    # 원래 청구기호 없고, 웹 스크래핑은 있는 책
    res = supabase.table("childbook_items") \
        .select("id, title, pangyo_callno, web_scraped_callno") \
        .is_("pangyo_callno", "null") \
        .not_.is_("web_scraped_callno", "null") \
        .neq("web_scraped_callno", "NotFound") \
        .execute()
    
    books = res.data
    
    print(f"✅ 원래 청구기호 없었는데 웹 스크래핑으로 찾은 책: {len(books)}권\n")
    
    if len(books) > 0:
        print("예시 (최대 10권):")
        for i, book in enumerate(books[:10], 1):
            print(f"{i}. {book['title']}")
            print(f"   웹 스크래핑: {book['web_scraped_callno']}\n")
    
    return len(books)

if __name__ == "__main__":
    count = check_new_callnos()
    print(f"\n💡 이 {count}권도 pangyo_callno에 업데이트하시겠어요?")
