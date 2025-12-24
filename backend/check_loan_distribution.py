"""대출 상태 분포 확인 스크립트"""
import asyncio
from collections import Counter
from core.database import supabase
from services.loan_status import fetch_loan_status_batch

async def check_loan_status_distribution():
    """대출 상태별 분포 확인"""
    
    print("📚 전체 도서 목록 조회 중...")
    # 판교 청구기호가 있는 모든 책 조회
    response = supabase.table("childbook_items")\
        .select("id, isbn, title, pangyo_callno")\
        .not_.is_("pangyo_callno", "null")\
        .execute()
    
    books = response.data
    print(f"✅ 총 {len(books)}권의 도서 조회 완료")
    
    # ISBN이 있는 책과 없는 책 구분
    books_with_isbn = [book for book in books if book.get('isbn') and book.get('isbn').strip()]
    books_without_isbn = [book for book in books if not book.get('isbn') or not book.get('isbn').strip()]
    
    print(f"\n📊 ISBN 통계:")
    print(f"  - ISBN 있음: {len(books_with_isbn)}권")
    print(f"  - ISBN 없음: {len(books_without_isbn)}권")
    
    if books_without_isbn:
        print(f"\n⚠️  ISBN 없는 책 샘플 (처음 5권):")
        for i, book in enumerate(books_without_isbn[:5], 1):
            print(f"  {i}. {book.get('title')} ({book.get('pangyo_callno')})")
    
    print(f"\n🔍 대출 상태 확인 중 (ISBN 있는 {len(books_with_isbn)}권)...")
    # 대출 상태 조회
    loan_statuses = await fetch_loan_status_batch(books_with_isbn)
    
    # 상태별 카운트
    status_counter = Counter()
    books_by_status = {
        '대출가능': [],
        '대출중': [],
        '미소장': [],
        '확인불가': [],
        '시간초과': [],
        '상태없음': []
    }
    
    for book in books_with_isbn:
        loan_status = loan_statuses.get(book['id'])
        if loan_status:
            status = loan_status.get('status', '상태없음')
            status_counter[status] += 1
            if status in books_by_status:
                books_by_status[status].append(book)
        else:
            status_counter['상태없음'] += 1
            books_by_status['상태없음'].append(book)
    
    print(f"\n📊 대출 상태 분포:")
    for status, count in status_counter.most_common():
        percentage = (count / len(books_with_isbn)) * 100
        print(f"  {status}: {count}권 ({percentage:.1f}%)")
    
    # 미소장 샘플 출력
    if books_by_status['미소장']:
        print(f"\n⚠️  미소장 도서 샘플 (처음 10권):")
        for i, book in enumerate(books_by_status['미소장'][:10], 1):
            print(f"  {i}. {book.get('title')} - {book.get('pangyo_callno')}")
    
    # 대출가능 샘플 출력
    if books_by_status['대출가능']:
        print(f"\n✅ 대출가능 도서 샘플 (처음 5권):")
        for i, book in enumerate(books_by_status['대출가능'][:5], 1):
            print(f"  {i}. {book.get('title')} - {book.get('pangyo_callno')}")

if __name__ == "__main__":
    asyncio.run(check_loan_status_distribution())
