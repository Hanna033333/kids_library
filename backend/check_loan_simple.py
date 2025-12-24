"""대출 상태 분포 확인 및 JSON 저장"""
import asyncio
import json
from collections import Counter
from core.database import supabase
from services.loan_status import fetch_loan_status_batch

async def check_loan_status_distribution():
    """대출 상태별 분포 확인"""
    
    print("Fetching books...")
    response = supabase.table("childbook_items")\
        .select("id, isbn, title, pangyo_callno")\
        .not_.is_("pangyo_callno", "null")\
        .execute()
    
    books = response.data
    print(f"Total books: {len(books)}")
    
    books_with_isbn = [book for book in books if book.get('isbn') and book.get('isbn').strip()]
    books_without_isbn = [book for book in books if not book.get('isbn') or not book.get('isbn').strip()]
    
    print(f"Books with ISBN: {len(books_with_isbn)}")
    print(f"Books without ISBN: {len(books_without_isbn)}")
    
    print(f"Checking loan status...")
    loan_statuses = await fetch_loan_status_batch(books_with_isbn)
    
    status_counter = Counter()
    
    for book in books_with_isbn:
        loan_status = loan_statuses.get(book['id'])
        if loan_status:
            status = loan_status.get('status', 'no_status')
            status_counter[status] += 1
        else:
            status_counter['no_status'] += 1
    
    result = {
        'total_books': len(books),
        'books_with_isbn': len(books_with_isbn),
        'books_without_isbn': len(books_without_isbn),
        'status_distribution': dict(status_counter)
    }
    
    with open('loan_status_summary.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nStatus distribution:")
    for status, count in status_counter.most_common():
        percentage = (count / len(books_with_isbn)) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    print(f"\nSaved to loan_status_summary.json")

if __name__ == "__main__":
    asyncio.run(check_loan_status_distribution())
