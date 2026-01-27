"""
전체 진단: 왜 DB 업데이트가 안 되는가?
"""
from supabase_client import supabase

print("=" * 60)
print("1. 현재 DB 상태 확인")
print("=" * 60)

# 카테고리별 분포
result = supabase.table('childbook_items').select('category').eq('curation_tag', '겨울방학2026').execute()

categories = {}
for book in result.data:
    cat = book.get('category')
    if cat is None:
        cat = 'NULL'
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count}권")

print(f"\n총 {len(result.data)}권")

print("\n" + "=" * 60)
print("2. 수동 업데이트 테스트")
print("=" * 60)

# NULL인 첫 번째 책 가져오기
null_books = supabase.table('childbook_items').select('id,title,category').eq('curation_tag', '겨울방학2026').is_('category', 'null').limit(1).execute()

if null_books.data:
    book = null_books.data[0]
    print(f"\n테스트 대상: {book['title']}")
    print(f"현재 카테고리: {book.get('category')}")
    
    # 업데이트 시도
    print("\n'테스트' 카테고리로 업데이트 시도...")
    try:
        update_result = supabase.table('childbook_items').update({
            'category': '테스트'
        }).eq('id', book['id']).execute()
        
        print(f"✅ 업데이트 성공")
        print(f"응답: {update_result.data}")
        
        # 다시 조회
        check = supabase.table('childbook_items').select('category').eq('id', book['id']).execute()
        print(f"\n재조회 결과: {check.data[0]['category']}")
        
        # 원래대로 복구
        supabase.table('childbook_items').update({'category': None}).eq('id', book['id']).execute()
        print("✅ 원래대로 복구 완료")
        
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
else:
    print("NULL인 책이 없습니다!")

print("\n" + "=" * 60)
print("3. recategorize_winter_safe.py 환경 변수 확인")
print("=" * 60)

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")

print(f"스크립트 위치: {current_dir}")
print(f".env 경로: {env_path}")
print(f".env 존재: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        print(f".env 라인 수: {len(lines)}")
        
        # SUPABASE_URL 확인
        for line in lines:
            if line.startswith("SUPABASE_URL"):
                url = line.split("=", 1)[1].strip().strip("'").strip('"')
                print(f"\nSUPABASE_URL: {url[:50]}...")
                print(f"supabase_client와 일치: {url == supabase.supabase_url}")
                break

print("\n" + "=" * 60)
print("진단 완료")
print("=" * 60)
