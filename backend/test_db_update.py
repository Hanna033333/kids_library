"""
한 권만 수동 테스트 (DB 업데이트 확인)
"""
import asyncio
from supabase_client import supabase
from recategorize_winter_safe import get_book_description, categorize_book_gpt

async def test_one_with_db():
    # 첫 번째 책
    result = supabase.table('childbook_items').select(
        'id,title,author,publisher,isbn,category'
    ).eq('curation_tag', '겨울방학2026').limit(1).execute()
    
    book = result.data[0]
    print(f"책: {book['title']}")
    print(f"현재 카테고리: {book.get('category')}")
    
    # 책 소개
    desc = await get_book_description(book.get('isbn'))
    
    # 분류
    category = await categorize_book_gpt(
        book['title'],
        book.get('author'),
        book.get('publisher'),
        desc
    )
    
    print(f"AI 분류: {category}")
    
    # DB 업데이트
    try:
        update_result = supabase.table('childbook_items').update({
            'category': category
        }).eq('id', book['id']).execute()
        
        print(f"✅ DB 업데이트 성공")
        print(f"업데이트된 데이터: {update_result.data}")
    except Exception as e:
        print(f"❌ DB 업데이트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_one_with_db())
