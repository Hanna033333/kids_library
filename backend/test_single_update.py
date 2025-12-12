"""단일 항목 테스트"""
from supabase_client import supabase

# CSV 첫 번째 항목 테스트
child_id = 8197
child_isbn = "9788954691550"

print(f"테스트: ID {child_id}, ISBN {child_isbn}")

# library_items에서 청구기호 찾기
res = supabase.table("library_items").select("isbn13,callno").eq("isbn13", child_isbn).limit(1).execute()

if res.data:
    callno = res.data[0].get("callno")
    print(f"찾은 청구기호: {callno}")
    
    # 업데이트 시도
    try:
        supabase.table("childbook_items").update({
            "pangyo_callno": callno
        }).eq("id", child_id).execute()
        print("✅ 업데이트 성공!")
    except Exception as e:
        print(f"❌ 업데이트 실패: {e}")
else:
    print("❌ library_items에서 찾지 못함")

