"""
단일 항목으로 ISBN 검색 테스트
"""
from supabase_client import supabase
from library_api import search_isbn_combined

# 둘 다 없는 항목 하나 가져오기
res = supabase.table("childbook_items").select("id,title,author,isbn,pangyo_callno").is_("isbn", "null").is_("pangyo_callno", "null").limit(1).execute()

if not res.data:
    print("처리 대상 항목이 없습니다.")
    exit(0)

item = res.data[0]
item_id = item.get("id")
title = item.get("title", "").strip()
author_raw = item.get("author", "").strip()

print("=" * 60)
print("단일 항목 테스트")
print("=" * 60)
print(f"ID: {item_id}")
print(f"제목: {title}")
print(f"저자: {author_raw}")
print()

# 저자 정보 정리
author = None
if author_raw:
    author_parts = author_raw.split("|")
    first_author = author_parts[0].strip()
    author_clean = first_author.replace("글", "").replace("그림", "").replace("옮김", "").replace(",", "").strip()
    if "," in author_clean:
        author_clean = author_clean.split(",")[0].strip()
    if author_clean:
        author = author_clean

print(f"정리된 저자: {author}")
print()

# ISBN 검색
print("ISBN 검색 중...")
try:
    isbn, score, source = search_isbn_combined(title, author)
    print(f"결과: ISBN={isbn}, 유사도={score}, 소스={source}")
    
    if not isbn or score < 30:
        print("저자 없이 재시도...")
        isbn, score, source = search_isbn_combined(title, None)
        print(f"결과: ISBN={isbn}, 유사도={score}, 소스={source}")
    
    if isbn and score >= 30:
        print(f"\n✅ ISBN 찾음: {isbn}")
        print("Supabase 업데이트 시도...")
        try:
            supabase.table("childbook_items").update({
                "isbn": isbn
            }).eq("id", item_id).execute()
            print("✅ 업데이트 성공!")
        except Exception as e:
            print(f"❌ 업데이트 실패: {e}")
    else:
        print(f"\n❌ ISBN을 찾지 못함 (유사도: {score})")
        
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

