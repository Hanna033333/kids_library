"""
로그 파일 저장 버전
"""
import asyncio
import sys
import os

# 로그 파일 열기
log_file = open("recategorize_detailed_log.txt", "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()

# recategorize_winter_safe.py 임포트
sys.path.insert(0, '.')
from recategorize_winter_safe import *

async def run_with_logging():
    log("=" * 80)
    log("재분류 시작 (로그 저장 모드)")
    log("=" * 80)
    
    # 도서 조회
    result = supabase.table('childbook_items').select(
        'id,title,category,author,publisher,isbn'
    ).eq('curation_tag', '겨울방학2026').limit(5).execute()  # 5권만 테스트
    
    books = result.data
    total = len(books)
    log(f"\n총 {total}권 처리\n")
    
    for i, book in enumerate(books, 1):
        try:
            log(f"[{i}/{total}] {book['title']}")
            log(f"  현재 카테고리: {book.get('category')}")
            
            # 책 소개
            desc = await get_book_description(book.get('isbn'))
            if desc:
                log(f"  책 소개: {desc[:50]}...")
            
            # 분류
            category = await categorize_book_gpt(
                book['title'],
                book.get('author'),
                book.get('publisher'),
                desc
            )
            
            log(f"  AI 분류: {category}")
            
            # DB 업데이트
            if category != book.get('category'):
                log(f"  DB 업데이트 시도...")
                try:
                    update_result = supabase.table('childbook_items').update({
                        'category': category
                    }).eq('id', book['id']).execute()
                    
                    log(f"  ✅ 업데이트 성공")
                    log(f"  응답 데이터: {update_result.data}")
                except Exception as e:
                    log(f"  ❌ 업데이트 실패: {e}")
                    import traceback
                    log(traceback.format_exc())
            else:
                log(f"  ℹ️ 변경 없음")
            
            log("")
            
        except Exception as e:
            log(f"  ❌ 에러: {e}")
            import traceback
            log(traceback.format_exc())
            continue
    
    log("=" * 80)
    log("완료")
    log("=" * 80)
    log_file.close()

if __name__ == "__main__":
    asyncio.run(run_with_logging())
