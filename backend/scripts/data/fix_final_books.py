from supabase_client import supabase

def fix_final_books():
    """마지막 3권 수정"""
    
    print("🔧 최종 수정 중...\n")
    
    # 1. 고릴라
    print("📚 고릴라 수정 중...")
    res = supabase.table("childbook_items") \
        .select("id") \
        .eq("title", "고릴라") \
        .execute()
    
    if res.data:
        book_id = res.data[0]['id']
        supabase.table("childbook_items").update({
            "isbn": "9788949110486",
            "pangyo_callno": "유 808.9-ㅂ966ㅂ-50=2",
            "web_scraped_callno": "유 808.9-ㅂ966ㅂ-50=2"
        }).eq("id", book_id).execute()
        print("   ✅ ISBN: 9788949110486")
        print("   ✅ 청구기호: 유 808.9-ㅂ966ㅂ-50=2\n")
    
    # 2. 장갑
    print("📚 장갑 수정 중...")
    res = supabase.table("childbook_items") \
        .select("id") \
        .eq("title", "장갑") \
        .execute()
    
    if res.data:
        book_id = res.data[0]['id']
        supabase.table("childbook_items").update({
            "isbn": "9788970941387",
            "pangyo_callno": "유 892.89-ㄹ244ㅈ2=2",
            "web_scraped_callno": "유 892.89-ㄹ244ㅈ2=2"
        }).eq("id", book_id).execute()
        print("   ✅ ISBN: 9788970941387")
        print("   ✅ 청구기호: 유 892.89-ㄹ244ㅈ2=2\n")
    
    # 3. 로베르토 -> 건축가 로베르토
    print("📚 로베르토 수정 중...")
    res = supabase.table("childbook_items") \
        .select("id") \
        .eq("title", "로베르토") \
        .execute()
    
    if res.data:
        book_id = res.data[0]['id']
        supabase.table("childbook_items").update({
            "title": "건축가 로베르토",
            "pangyo_callno": "유 808.9-ㅍ12ㅍ-v.46",
            "web_scraped_callno": "유 808.9-ㅍ12ㅍ-v.46"
        }).eq("id", book_id).execute()
        print("   ✅ 제목: 건축가 로베르토")
        print("   ✅ 청구기호: 유 808.9-ㅍ12ㅍ-v.46\n")
    
    print("✅ 모든 수정 완료!")

if __name__ == "__main__":
    fix_final_books()
