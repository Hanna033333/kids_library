from supabase_client import supabase

def hide_unowned_books():
    """미소장 책(pangyo_callno가 NULL인 책) 숨기기"""
    
    print("📊 미소장 책 확인 중...\n")
    
    # pangyo_callno가 NULL인 책 수 확인
    res = supabase.table("childbook_items") \
        .select("*", count="exact", head=True) \
        .is_("pangyo_callno", "null") \
        .execute()
    
    count = res.count
    print(f"미소장 책: {count}권")
    
    if count == 0:
        print("미소장 책이 없습니다.")
        return
    
    # is_hidden = true로 업데이트
    print(f"\n{count}권을 숨김 처리 중...")
    
    supabase.table("childbook_items") \
        .update({"is_hidden": True}) \
        .is_("pangyo_callno", "null") \
        .execute()
    
    print(f"✅ {count}권 숨김 처리 완료!")

if __name__ == "__main__":
    hide_unowned_books()
