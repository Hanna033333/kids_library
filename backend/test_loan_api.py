"""대출 정보 API 테스트"""
import asyncio
from services.loan_status import fetch_loan_status_batch

# 테스트용 책 데이터 (실제 ISBN이 있는 책)
test_books = [
    {"id": 1, "isbn": "9788936446819"},  # 테스트 ISBN
    {"id": 2, "isbn": "9788937460449"},  # 어린왕자
]

async def test():
    print("📚 대출 정보 API 테스트 시작...")
    print(f"테스트 책 수: {len(test_books)}")
    
    result = await fetch_loan_status_batch(test_books)
    
    print(f"\n✅ 결과:")
    for book_id, loan_info in result.items():
        print(f"  Book ID {book_id}: {loan_info}")
    
    if not result:
        print("⚠️  결과가 비어있습니다!")
    
    return result

if __name__ == "__main__":
    asyncio.run(test())

