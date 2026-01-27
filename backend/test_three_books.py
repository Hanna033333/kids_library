"""
샘플 3권만 다시 테스트 (로그 확인용)
"""
import asyncio
import sys
sys.path.insert(0, '.')

from recategorize_winter_safe import *

async def test_three():
    # 3권만 가져오기
    result = supabase.table('childbook_items').select(
        'id,title,author,publisher,isbn,category'
    ).eq('curation_tag', '겨울방학2026').limit(3).execute()
    
    for i, book in enumerate(result.data, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/3] {book['title']}")
        print(f"현재 DB 카테고리: {book.get('category')}")
        
        # 책 소개
        desc = await get_book_description(book.get('isbn'))
        if desc:
            print(f"책 소개: {desc[:100]}...")
        
        # 분류
        category = await categorize_book_gpt(
            book['title'],
            book.get('author'),
            book.get('publisher'),
            desc
        )
        
        print(f"AI 분류 결과: {category}")
        print('='*60)

if __name__ == "__main__":
    asyncio.run(test_three())
