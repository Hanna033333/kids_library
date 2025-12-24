"""미소장 제외 도서의 권차 기호 조회"""
import asyncio
import aiohttp
import csv
from core.database import supabase
from core.config import DATA4LIBRARY_KEY
from services.loan_status import fetch_loan_status_batch

PANGYO_LIB_CODE = "141231"

async def fetch_volume_info(session, isbn, title):
    """ISBN으로 권차 정보 조회"""
    url = "http://data4library.kr/api/itemSrch"
    params = {
        "authKey": DATA4LIBRARY_KEY,
        "libCode": PANGYO_LIB_CODE,
        "isbn13": isbn,
        "format": "json",
        "pageSize": 100
    }
    
    try:
        async with session.get(url, params=params, timeout=10) as response:
            data = await response.json()
            
            result = data.get("response", {}).get("result", [])
            if not result:
                return None
            
            # 여러 권이 있을 수 있음
            volumes = []
            for item in result:
                vol = item.get("vol", "")
                if vol:
                    volumes.append(vol)
            
            return volumes if volumes else None
            
    except Exception as e:
        print(f"Error fetching volume for {title}: {e}")
        return None

async def check_volumes_for_owned_books():
    """미소장 제외 도서의 권차 정보 조회"""
    
    print("📚 전체 도서 목록 조회 중...")
    response = supabase.table("childbook_items")\
        .select("id, isbn, title, author, pangyo_callno")\
        .not_.is_("pangyo_callno", "null")\
        .execute()
    
    books = response.data
    books_with_isbn = [book for book in books if book.get('isbn') and book.get('isbn').strip()]
    
    print(f"✅ ISBN 있는 도서: {len(books_with_isbn)}권")
    
    print("\n🔍 대출 상태 확인 중...")
    loan_statuses = await fetch_loan_status_batch(books_with_isbn)
    
    # 미소장이 아닌 책만 필터링
    owned_books = []
    not_owned_count = 0
    
    for book in books_with_isbn:
        loan_status = loan_statuses.get(book['id'])
        if loan_status:
            status = loan_status.get('status', '')
            if status == '미소장':
                not_owned_count += 1
            else:
                owned_books.append(book)
        else:
            owned_books.append(book)
    
    print(f"✅ 소장 도서: {len(owned_books)}권")
    print(f"⚠️  미소장 도서: {not_owned_count}권 (제외)")
    
    print(f"\n🔍 권차 정보 조회 중 ({len(owned_books)}권)...")
    
    # 권차 정보 조회
    results = []
    semaphore = asyncio.Semaphore(10)  # 동시 요청 제한
    
    async def fetch_with_sem(session, book):
        async with semaphore:
            volumes = await fetch_volume_info(session, book['isbn'], book['title'])
            return {
                'id': book['id'],
                'isbn': book['isbn'],
                'title': book['title'],
                'author': book.get('author', ''),
                'pangyo_callno': book['pangyo_callno'],
                'volumes': volumes,
                'volume_count': len(volumes) if volumes else 0
            }
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_sem(session, book) for book in owned_books]
        results = await asyncio.gather(*tasks)
    
    # 권차가 있는 책만 필터링
    books_with_volumes = [r for r in results if r['volumes']]
    books_without_volumes = [r for r in results if not r['volumes']]
    
    print(f"\n📊 권차 정보 결과:")
    print(f"  - 권차 있음: {len(books_with_volumes)}권")
    print(f"  - 권차 없음: {len(books_without_volumes)}권")
    
    # CSV 저장
    output_file = 'books_with_volumes.csv'
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['ISBN', '제목', '작가', '청구기호', '권차 목록', '권수'])
        
        for book in books_with_volumes:
            volumes_str = ', '.join(book['volumes'])
            writer.writerow([
                book['isbn'],
                book['title'],
                book['author'],
                book['pangyo_callno'],
                volumes_str,
                book['volume_count']
            ])
    
    print(f"\n✅ CSV 저장 완료: {output_file}")
    
    # 샘플 출력
    if books_with_volumes:
        print(f"\n📋 권차 있는 책 샘플 (처음 10권):")
        for i, book in enumerate(books_with_volumes[:10], 1):
            volumes_str = ', '.join(book['volumes'])
            print(f"{i}. {book['title']} - 권차: {volumes_str}")

if __name__ == "__main__":
    asyncio.run(check_volumes_for_owned_books())
