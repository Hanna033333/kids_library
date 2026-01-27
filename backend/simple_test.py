"""
간단 테스트: 3권만 처리 (에러 확인용)
"""
import asyncio
import sys
sys.path.insert(0, '.')

from recategorize_winter_safe import *

async def test_three_books():
    print("3권 테스트 시작...\n")
    
    # 3권만 가져오기
    result = supabase.table('childbook_items').select(
        'id,title,author,publisher,isbn,category'
    ).eq('curation_tag', '겨울방학2026').limit(3).execute()
    
    for i, book in enumerate(result.data, 1):
        try:
            print(f"[{i}/3] {book['title']}")
            
            # 책 소개
            desc = await get_book_description(book.get('isbn'))
            
            # 분류
            category = await categorize_book_gpt(
                book['title'],
                book.get('author'),
                book.get('publisher'),
                desc
            )
            
            print(f"  결과: {category}")
            
            # DB 업데이트
            if category != book.get('category'):
                supabase.table('childbook_items').update({
                    'category': category
                }).eq('id', book['id']).execute()
                print(f"  ✅ 업데이트 완료\n")
            else:
                print(f"  ℹ️ 변경 없음\n")
                
        except Exception as e:
            print(f"  ❌ 에러: {e}\n")
            import traceback
            traceback.print_exc()
            continue

if __name__ == "__main__":
    asyncio.run(test_three_books())
