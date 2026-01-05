from supabase_client import supabase

# 책 정보 확인
res = supabase.table("childbook_items") \
    .select("*") \
    .eq("id", 8882) \
    .execute()

if res.data:
    book = res.data[0]
    print("컬럼 목록:")
    for key in book.keys():
        if 'cover' in key.lower() or 'image' in key.lower():
            print(f"  {key}: {book[key]}")
