from supabase_client import supabase

def check_descriptions():
    """도서 소개 데이터 확인"""
    print("도서 소개 데이터 분석 중...")
    print()
    
    # 전체 책 수
    total_res = supabase.table("childbook_items") \
        .select("*", count="exact", head=True) \
        .execute()
    total = total_res.count
    
    # description이 있는 책
    with_desc_res = supabase.table("childbook_items") \
        .select("*", count="exact", head=True) \
        .not_.is_("description", "null") \
        .neq("description", "") \
        .execute()
    with_desc = with_desc_res.count
    
    # description이 없는 책
    without_desc = total - with_desc
    
    print(f"총 책 수: {total}권")
    print(f"도서 소개 있음: {with_desc}권 ({with_desc*100//total}%)")
    print(f"도서 소개 없음: {without_desc}권 ({without_desc*100//total}%)")

if __name__ == "__main__":
    check_descriptions()
