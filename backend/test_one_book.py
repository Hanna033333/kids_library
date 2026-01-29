"""
한 권만 테스트 (디버그 모드)
"""
import asyncio
import sys
sys.path.insert(0, '.')

# recategorize_winter_safe.py의 함수들을 임포트
import importlib.util
spec = importlib.util.spec_from_file_location("recategorize", "recategorize_winter_safe.py")
recategorize = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recategorize)

async def test_one():
    from supabase_client import supabase
    
    # 첫 번째 책 가져오기
    result = supabase.table('childbook_items').select(
        'id,title,author,publisher,isbn,category'
    ).eq('curation_tag', '겨울방학2026').limit(1).execute()
    
    if not result.data:
        print("책 없음")
        return
    
    book = result.data[0]
    print(f"\n테스트 도서: {book['title']}")
    print(f"현재 카테고리: {book.get('category')}")
    print(f"ISBN: {book.get('isbn')}")
    print("="*60)
    
    # 책 소개 가져오기
    description = await recategorize.get_book_description(book.get('isbn'))
    if description:
        print(f"\n📖 책 소개:\n{description[:200]}...")
    else:
        print("\n📖 책 소개: 없음")
    
    print("\n" + "="*60)
    print("AI 분류 시작...")
    print("="*60)
    
    # 분류
    category = await recategorize.categorize_book_gpt(
        book['title'],
        book.get('author'),
        book.get('publisher'),
        description
    )
    
    print("="*60)
    print(f"\n✅ 최종 결과: {category}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_one())
