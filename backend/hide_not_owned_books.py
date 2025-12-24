"""미소장 확정 도서를 숨김 처리"""
import csv
from core.database import supabase

# CSV에서 ID 목록 가져오기
book_ids = []
with open('confirmed_not_owned_books.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    # ID가 없으므로 제목으로 다시 조회해야 함
    titles = [row['title'] for row in reader]

print(f"숨김 처리할 책: {len(titles)}권")

# 제목으로 ID 조회
response = supabase.table("childbook_items")\
    .select("id, title")\
    .in_("title", titles)\
    .execute()

book_ids = [book['id'] for book in response.data]
print(f"DB에서 찾은 책: {len(book_ids)}권")

# is_hidden 컬럼이 있는지 확인하고 없으면 추가
# Supabase에서는 직접 ALTER TABLE을 할 수 없으므로, 
# 먼저 테스트로 업데이트 시도
try:
    # 테스트 업데이트
    test_result = supabase.table("childbook_items")\
        .update({"is_hidden": True})\
        .eq("id", book_ids[0])\
        .execute()
    
    print("✅ is_hidden 컬럼 존재 확인")
    
    # 전체 업데이트
    for i in range(0, len(book_ids), 100):
        batch = book_ids[i:i+100]
        supabase.table("childbook_items")\
            .update({"is_hidden": True})\
            .in_("id", batch)\
            .execute()
        print(f"  처리 중: {i+len(batch)}/{len(book_ids)}")
    
    print(f"\n✅ {len(book_ids)}권 숨김 처리 완료")
    
except Exception as e:
    print(f"\n❌ 오류: {e}")
    print("\n⚠️  is_hidden 컬럼이 없습니다!")
    print("Supabase 대시보드에서 다음 SQL을 실행해주세요:")
    print("\nALTER TABLE childbook_items ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE;")
    print("\n실행 후 이 스크립트를 다시 실행하세요.")
