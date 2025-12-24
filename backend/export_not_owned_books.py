"""미소장 도서 목록 추출 스크립트"""
import asyncio
import csv
from core.database import supabase
from services.loan_status import fetch_loan_status_batch

async def export_not_owned_books():
    """미소장 상태인 책들을 CSV로 추출"""
    
    print("📚 전체 도서 목록 조회 중...")
    # 판교 청구기호가 있는 모든 책 조회
    response = supabase.table("childbook_items")\
        .select("id, isbn, title, author, publisher, pangyo_callno")\
        .not_.is_("pangyo_callno", "null")\
        .order("pangyo_callno")\
        .execute()
    
    books = response.data
    print(f"✅ 총 {len(books)}권의 도서 조회 완료")
    
    # ISBN이 있는 책만 필터링
    books_with_isbn = [book for book in books if book.get('isbn')]
    print(f"📖 ISBN이 있는 도서: {len(books_with_isbn)}권")
    
    print("\n🔍 대출 상태 확인 중...")
    # 대출 상태 조회 (배치 처리)
    loan_statuses = await fetch_loan_status_batch(books_with_isbn)
    
    # 미소장 도서만 필터링
    not_owned_books = []
    for book in books_with_isbn:
        loan_status = loan_statuses.get(book['id'])
        if loan_status and loan_status.get('status') == '미소장':
            not_owned_books.append({
                'isbn': book.get('isbn', ''),
                'title': book.get('title', ''),
                'author': book.get('author', ''),
                'publisher': book.get('publisher', ''),
                'pangyo_callno': book.get('pangyo_callno', ''),
                'status': loan_status.get('status', '')
            })
    
    print(f"\n⚠️  미소장 도서: {len(not_owned_books)}권")
    
    # CSV 파일로 저장
    output_file = 'not_owned_books.csv'
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['isbn', 'title', 'author', 'publisher', 'pangyo_callno', 'status'])
        writer.writeheader()
        writer.writerows(not_owned_books)
    
    print(f"\n✅ CSV 파일 저장 완료: {output_file}")
    print(f"📊 총 {len(not_owned_books)}권의 미소장 도서가 추출되었습니다.")
    
    # 샘플 출력
    if not_owned_books:
        print("\n📋 샘플 (처음 5권):")
        for i, book in enumerate(not_owned_books[:5], 1):
            print(f"{i}. {book['title']} - {book['author']} ({book['pangyo_callno']})")

if __name__ == "__main__":
    asyncio.run(export_not_owned_books())
