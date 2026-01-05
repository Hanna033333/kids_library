from supabase_client import supabase

def analyze_remaining():
    """나머지 책들 분석"""
    print("📊 나머지 책 분석 중...\n")
    
    # 전체 책 수
    total_res = supabase.table("childbook_items") \
        .select("*", count="exact", head=True) \
        .execute()
    total = total_res.count
    
    # 웹 스크래핑 결과별 분류
    # 1. NotFound (판교도서관에 없음)
    not_found_res = supabase.table("childbook_items") \
        .select("*", count="exact", head=True) \
        .eq("web_scraped_callno", "NotFound") \
        .execute()
    not_found = not_found_res.count
    
    # 2. NULL (스크래핑 안 함)
    null_res = supabase.table("childbook_items") \
        .select("*", count="exact", head=True) \
        .is_("web_scraped_callno", "null") \
        .execute()
    null_count = null_res.count
    
    # 3. 청구기호 있음
    found_res = supabase.table("childbook_items") \
        .select("*", count="exact", head=True) \
        .not_.is_("web_scraped_callno", "null") \
        .neq("web_scraped_callno", "NotFound") \
        .execute()
    found = found_res.count
    
    print(f"📚 전체 분석 결과")
    print(f"=" * 50)
    print(f"총 책 수: {total}권")
    print(f"")
    print(f"✅ 청구기호 찾음: {found}권")
    print(f"❌ NotFound (판교도서관에 없음): {not_found}권")
    print(f"⚠️  스크래핑 안 함 (NULL): {null_count}권")
    print(f"")
    print(f"검증: {found} + {not_found} + {null_count} = {found + not_found + null_count}")

if __name__ == "__main__":
    analyze_remaining()
