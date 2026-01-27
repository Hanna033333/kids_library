"""
겨울방학2026 도서 일괄 재분류 스크립트

모든 겨울방학 도서의 카테고리를 AI로 재분류합니다.
"""
import asyncio
import sys
import os

# 현재 디렉토리를 path에 추가하여 모듈 import 문제 해결
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from add_book_with_category import update_book_category
from supabase_client import supabase


async def recategorize_winter_books():
    """겨울방학2026 도서 일괄 재분류"""
    
    print("=" * 80)
    print("겨울방학2026 도서 일괄 재분류")
    print("=" * 80)
    
    # 1. 겨울방학2026 도서 조회
    result = supabase.table('childbook_items').select(
        'id,title,category'
    ).eq('curation_tag', '겨울방학2026').execute()
    
    if not result.data:
        print("❌ 겨울방학2026 도서를 찾을 수 없습니다.")
        return
    
    total = len(result.data)
    print(f"\n📚 총 {total}권의 도서를 재분류합니다.\n")
    
    # 2. 각 도서 재분류
    success_count = 0
    failed_books = []
    category_changes = {}
    
    for i, book in enumerate(result.data, 1):
        book_id = book['id']
        title = book['title']
        old_category = book.get('category', 'N/A')
        
        print(f"[{i}/{total}] {title}")
        print(f"  현재 카테고리: {old_category}")
        
        try:
            # force_recategorize=True로 설정하여 기존 카테고리 무시하고 재분류
            new_category = await update_book_category(book_id, force_recategorize=True)
            
            if new_category:
                if new_category != old_category:
                    change_key = f"{old_category} → {new_category}"
                    category_changes[change_key] = category_changes.get(change_key, 0) + 1
                    print(f"  ✅ 변경됨: {old_category} → {new_category}")
                else:
                    print(f"  ℹ️  변경 없음: {new_category}")
                success_count += 1
            else:
                print(f"  ❌ 재분류 실패")
                failed_books.append(title)
                
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            failed_books.append(title)
        
        print()
        
        # API 호출 제한 고려 (Gemini 무료: 분당 15 requests)
        # 4초 대기 (더 안전하게)
        await asyncio.sleep(4)
    
    # 3. 결과 요약
    print("=" * 80)
    print("재분류 완료!")
    print("=" * 80)
    print(f"\n✅ 성공: {success_count}/{total}권")
    
    if failed_books:
        print(f"❌ 실패: {len(failed_books)}권")
        print("  실패한 도서:")
        for book in failed_books:
            print(f"  - {book}")
    
    if category_changes:
        print(f"\n📊 카테고리 변경 내역:")
        for change, count in sorted(category_changes.items(), key=lambda x: x[1], reverse=True):
            print(f"  {change}: {count}권")
    
    print("\n" + "=" * 80)
    
    # 4. 최종 카테고리 분포 확인
    final_result = supabase.table('childbook_items').select(
        'category'
    ).eq('curation_tag', '겨울방학2026').execute()
    
    categories = {}
    for book in final_result.data:
        cat = book.get('category', 'N/A')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 재분류 후 카테고리 분포:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}권")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(recategorize_winter_books())
