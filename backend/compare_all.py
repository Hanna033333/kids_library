from supabase_client import supabase

def compare_all_callnos():
    print("전체 청구기호 비교 중...\n")
    
    # 모든 책 조회
    res = supabase.table("childbook_items") \
        .select("pangyo_callno, web_scraped_callno") \
        .execute()
    
    books = res.data
    total = len(books)
    
    same = 0
    different = 0
    
    for book in books:
        original = book.get('pangyo_callno')
        scraped = book.get('web_scraped_callno')
        
        # NULL/NotFound 처리
        if not original:
            original = None
        if not scraped or scraped == 'NotFound':
            scraped = None
            
        # 둘 다 있을 때만 비교
        if original and scraped:
            if original == scraped:
                same += 1
            else:
                different += 1
    
    print(f"📊 전체 청구기호 비교 결과")
    print(f"=" * 50)
    print(f"총 책 수: {total}권")
    print(f"")
    print(f"✅ 동일: {same}권")
    print(f"⚠️  다름: {different}권")
    print(f"")
    print(f"비율: {different/(same+different)*100:.1f}% 다름")

if __name__ == "__main__":
    compare_all_callnos()
