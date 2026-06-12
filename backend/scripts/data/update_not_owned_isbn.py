"""미소장 도서의 ISBN 재조회 (알라딘 API)"""
import asyncio
import aiohttp
import csv
from core.database import supabase
from core.config import ALADIN_TTB_KEY
from services.loan_status import fetch_loan_status_batch

async def fetch_isbn_from_aladin(session, title, author):
    """알라딘 API로 ISBN 조회"""
    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "ttbkey": ALADIN_TTB_KEY,
        "Query": title,
        "QueryType": "Title",
        "MaxResults": 5,
        "start": 1,
        "SearchTarget": "Book",
        "output": "js",
        "Version": "20131101"
    }
    
    try:
        async with session.get(url, params=params, timeout=10) as response:
            data = await response.json()
            items = data.get("item", [])
            
            if not items:
                return None
            
            # 제목과 저자로 매칭
            for item in items:
                api_title = item.get("title", "")
                api_author = item.get("author", "")
                api_isbn = item.get("isbn13", "")
                
                # 제목이 포함되어 있으면 매칭
                if title[:10] in api_title or api_title[:10] in title:
                    return {
                        "isbn13": api_isbn,
                        "title": api_title,
                        "author": api_author,
                        "publisher": item.get("publisher", "")
                    }
            
            # 매칭 실패 시 첫 번째 결과 반환
            return {
                "isbn13": items[0].get("isbn13", ""),
                "title": items[0].get("title", ""),
                "author": items[0].get("author", ""),
                "publisher": items[0].get("publisher", "")
            }
            
    except Exception as e:
        print(f"Error for {title}: {e}")
        return None

async def update_not_owned_isbn():
    """미소장 도서의 ISBN 재조회 및 업데이트"""
    
    print("📚 전체 도서 목록 조회 중...")
    response = supabase.table("childbook_items")\
        .select("id, isbn, title, author, publisher, pangyo_callno")\
        .not_.is_("pangyo_callno", "null")\
        .execute()
    
    books = response.data
    books_with_isbn = [book for book in books if book.get('isbn') and book.get('isbn').strip()]
    
    print(f"✅ ISBN 있는 도서: {len(books_with_isbn)}권")
    
    print("\n🔍 대출 상태 확인 중...")
    loan_statuses = await fetch_loan_status_batch(books_with_isbn)
    
    # 미소장 도서만 필터링
    not_owned_books = []
    for book in books_with_isbn:
        loan_status = loan_statuses.get(book['id'])
        if loan_status and loan_status.get('status') == '미소장':
            not_owned_books.append(book)
    
    print(f"⚠️  미소장 도서: {len(not_owned_books)}권")
    
    print(f"\n🔍 알라딘 API로 ISBN 재조회 중...")
    print("(이 작업은 약 2-3분 소요될 수 있습니다...)")
    
    results = []
    updated_count = 0
    failed_count = 0
    semaphore = asyncio.Semaphore(5)  # 알라딘 API는 느리므로 동시 요청 제한
    
    async def process_book(session, book, index):
        nonlocal updated_count, failed_count
        
        async with semaphore:
            if index % 10 == 0:
                print(f"  진행 중: {index}/{len(not_owned_books)} (성공: {updated_count}, 실패: {failed_count})")
            
            aladin_result = await fetch_isbn_from_aladin(session, book['title'], book.get('author', ''))
            await asyncio.sleep(0.5)  # 알라딘 API Rate limiting
            
            result = {
                'id': book['id'],
                'old_isbn': book.get('isbn', ''),
                'title': book['title'],
                'author': book.get('author', ''),
                'publisher': book.get('publisher', ''),
                'pangyo_callno': book['pangyo_callno']
            }
            
            if aladin_result:
                new_isbn = aladin_result['isbn13']
                result['new_isbn'] = new_isbn
                result['aladin_title'] = aladin_result['title']
                result['aladin_author'] = aladin_result['author']
                result['aladin_publisher'] = aladin_result['publisher']
                
                # ISBN이 다르면 업데이트
                if new_isbn and new_isbn != book.get('isbn'):
                    try:
                        supabase.table("childbook_items")\
                            .update({"isbn": new_isbn})\
                            .eq("id", book['id'])\
                            .execute()
                        result['updated'] = True
                        updated_count += 1
                    except Exception as e:
                        result['updated'] = False
                        result['error'] = str(e)
                        failed_count += 1
                else:
                    result['updated'] = False
                    result['reason'] = 'Same ISBN'
            else:
                result['new_isbn'] = ''
                result['updated'] = False
                result['reason'] = 'Not found in Aladin'
                failed_count += 1
            
            return result
    
    async with aiohttp.ClientSession() as session:
        tasks = [process_book(session, book, i) for i, book in enumerate(not_owned_books, 1)]
        results = await asyncio.gather(*tasks)
    
    # CSV 저장
    output_file = 'not_owned_isbn_update.csv'
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['id', 'title', 'old_isbn', 'new_isbn', 'updated', 'aladin_title', 'aladin_author', 'aladin_publisher', 'reason']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n{'='*60}")
    print(f"✅ 총 {updated_count}권 ISBN 업데이트 완료")
    print(f"❌ 업데이트 실패/불필요: {failed_count}권")
    print(f"📄 결과 CSV: {output_file}")
    print(f"{'='*60}")
    
    # 업데이트된 책 샘플
    updated_books = [r for r in results if r.get('updated')]
    if updated_books:
        print(f"\n📋 업데이트된 책 샘플 (처음 5권):")
        for i, book in enumerate(updated_books[:5], 1):
            print(f"{i}. {book['title']}")
            print(f"   Old ISBN: {book['old_isbn']}")
            print(f"   New ISBN: {book['new_isbn']}")

if __name__ == "__main__":
    asyncio.run(update_not_owned_isbn())
