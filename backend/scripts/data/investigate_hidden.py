"""is_hidden 상태 조사"""
from core.database import supabase

# 1. 전체 통계
print("=== 전체 통계 ===")
total = supabase.table("childbook_items").select("id", count="exact").execute()
print(f"전체 도서: {total.count}권")

with_callno = supabase.table("childbook_items").select("id", count="exact").not_.is_("pangyo_callno", "null").execute()
print(f"청구기호 있음: {with_callno.count}권")

# 2. is_hidden 상태별
print("\n=== is_hidden 상태별 ===")
hidden_true = supabase.table("childbook_items").select("id", count="exact").eq("is_hidden", True).execute()
print(f"is_hidden = True: {hidden_true.count}권")

hidden_false = supabase.table("childbook_items").select("id", count="exact").eq("is_hidden", False).execute()
print(f"is_hidden = False: {hidden_false.count}권")

hidden_null = supabase.table("childbook_items").select("id", count="exact").is_("is_hidden", "null").execute()
print(f"is_hidden = NULL: {hidden_null.count}권")

# 3. 프론트엔드 쿼리 시뮬레이션
print("\n=== 프론트엔드 쿼리 시뮬레이션 ===")
query = supabase.table("childbook_items").select("*", count="exact")
query = query.not_.is_("pangyo_callno", "null")
query = query.neq("pangyo_callno", "없음")
query = query.or_("is_hidden.is.null,is_hidden.eq.false")
result = query.execute()

print(f"프론트엔드에서 보여야 할 책: {result.count}권")
print(f"실제 데이터 개수: {len(result.data)}권")

# 4. is_hidden=True인 책 샘플
print("\n=== is_hidden=True 책 샘플 (처음 10권) ===")
hidden_books = supabase.table("childbook_items")\
    .select("id, title, isbn, pangyo_callno, is_hidden")\
    .eq("is_hidden", True)\
    .limit(10)\
    .execute()

for i, book in enumerate(hidden_books.data, 1):
    print(f"{i}. {book['title']} - {book['pangyo_callno']}")
