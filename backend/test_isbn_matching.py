"""
ISBN 매칭 테스트
"""
from supabase_client import supabase

# childbook_items에서 ISBN이 있는 항목 하나 가져오기
child_res = supabase.table("childbook_items").select("id,isbn,title").not_.is_("isbn", "null").limit(5).execute()

print("=" * 60)
print("ISBN 매칭 테스트")
print("=" * 60)
print()

for child_item in child_res.data:
    child_id = child_item.get("id")
    child_isbn = child_item.get("isbn")
    child_title = child_item.get("title", "")
    
    print(f"Child ID: {child_id}")
    print(f"  ISBN: {child_isbn}")
    print(f"  제목: {child_title[:50]}")
    
    # ISBN 정규화
    child_isbn_normalized = ''.join(filter(str.isdigit, str(child_isbn)))
    print(f"  정규화된 ISBN: {child_isbn_normalized} (길이: {len(child_isbn_normalized)})")
    
    # library_items에서 매칭 시도
    lib_res = supabase.table("library_items").select("isbn13,callno,title").eq("isbn13", child_isbn_normalized).limit(1).execute()
    
    if lib_res.data:
        lib_item = lib_res.data[0]
        print(f"  ✅ 매칭됨!")
        print(f"     library_items ISBN13: {lib_item.get('isbn13')}")
        print(f"     callno: {lib_item.get('callno')}")
    else:
        # ISBN-13으로 직접 검색
        if len(child_isbn_normalized) == 13:
            lib_res2 = supabase.table("library_items").select("isbn13,callno,title").limit(100).execute()
            found = False
            for lib_item in lib_res2.data:
                lib_isbn = lib_item.get("isbn13")
                if lib_isbn:
                    lib_isbn_normalized = ''.join(filter(str.isdigit, str(lib_isbn)))
                    if child_isbn_normalized == lib_isbn_normalized:
                        print(f"  ✅ 매칭됨! (수동 검색)")
                        print(f"     library_items ISBN13: {lib_isbn}")
                        print(f"     callno: {lib_item.get('callno')}")
                        found = True
                        break
            if not found:
                print(f"  ❌ 매칭 안됨")
        else:
            print(f"  ❌ ISBN 형식이 맞지 않음 (13자리 아님)")
    
    print()

