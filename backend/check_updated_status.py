"""ISBN 업데이트된 22권의 대출 상태 재확인"""
import asyncio
import csv
from core.database import supabase
from services.loan_status import fetch_loan_status_batch

async def check_updated_books_status():
    """ISBN 업데이트된 책들의 대출 상태 확인"""
    
    print("📚 업데이트된 책 목록 불러오는 중...")
    
    # CSV에서 업데이트된 책 ID 가져오기
    updated_ids = []
    with open('not_owned_isbn_update.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('updated') == 'True':
                updated_ids.append(int(row['id']))
    
    print(f"✅ 업데이트된 책: {len(updated_ids)}권")
    
    # DB에서 해당 책들 조회
    response = supabase.table("childbook_items")\
        .select("id, isbn, title, author, pangyo_callno")\
        .in_("id", updated_ids)\
        .execute()
    
    books = response.data
    print(f"📖 DB 조회 완료: {len(books)}권")
    
    print("\n🔍 대출 상태 확인 중...")
    loan_statuses = await fetch_loan_status_batch(books)
    
    # 상태별 분류
    available = []
    on_loan = []
    not_owned = []
    other = []
    
    for book in books:
        loan_status = loan_statuses.get(book['id'])
        status = loan_status.get('status', '확인불가') if loan_status else '확인불가'
        
        book_info = {
            'id': book['id'],
            'isbn': book['isbn'],
            'title': book['title'],
            'author': book.get('author', ''),
            'pangyo_callno': book['pangyo_callno'],
            'status': status
        }
        
        if status == '대출가능':
            available.append(book_info)
        elif status == '대출중':
            on_loan.append(book_info)
        elif status == '미소장':
            not_owned.append(book_info)
        else:
            other.append(book_info)
    
    print(f"\n{'='*60}")
    print(f"📊 대출 상태 결과:")
    print(f"  ✅ 대출가능: {len(available)}권")
    print(f"  📚 대출중: {len(on_loan)}권")
    print(f"  ⚠️  미소장: {len(not_owned)}권")
    print(f"  ❓ 기타: {len(other)}권")
    print(f"{'='*60}")
    
    # 대출가능 책 출력
    if available:
        print(f"\n✅ 대출가능한 책 ({len(available)}권):")
        for i, book in enumerate(available, 1):
            print(f"{i}. {book['title']} - {book['author']}")
            print(f"   ISBN: {book['isbn']}, 청구기호: {book['pangyo_callno']}")
    
    # 대출중 책 출력
    if on_loan:
        print(f"\n📚 대출중인 책 ({len(on_loan)}권):")
        for i, book in enumerate(on_loan, 1):
            print(f"{i}. {book['title']} - {book['author']}")
            print(f"   ISBN: {book['isbn']}, 청구기호: {book['pangyo_callno']}")
    
    # 여전히 미소장인 책 출력
    if not_owned:
        print(f"\n⚠️  여전히 미소장인 책 ({len(not_owned)}권):")
        for i, book in enumerate(not_owned, 1):
            print(f"{i}. {book['title']} - {book['author']}")
            print(f"   ISBN: {book['isbn']}, 청구기호: {book['pangyo_callno']}")
    
    # 결과 CSV 저장
    all_results = available + on_loan + not_owned + other
    output_file = 'updated_books_loan_status.csv'
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'isbn', 'title', 'author', 'pangyo_callno', 'status'])
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"\n📄 결과 CSV 저장: {output_file}")

if __name__ == "__main__":
    asyncio.run(check_updated_books_status())
