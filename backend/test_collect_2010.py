from crawler import fetch_library_books_child
import time

print("=" * 60)
print("판교 도서관 아동 도서 수집 시작")
print("기간: 2010-01-01 ~ 2025-12-31")
print("=" * 60)
print()

start_time = time.time()

books = fetch_library_books_child('2010-01-01', '2025-12-31')

end_time = time.time()
elapsed_time = end_time - start_time

print()
print("=" * 60)
print(f"수집 완료!")
print(f"총 수집된 아동 도서: {len(books)}권")
print(f"소요 시간: {elapsed_time:.2f}초 ({elapsed_time/60:.2f}분)")
print("=" * 60)

if books:
    print(f"\n첫 10개 샘플:")
    for i, book in enumerate(books[:10], 1):
        print(f"{i}. {book['title']} - {book['author']} (분류번호: {book['kdc']}, ISBN: {book['isbn13']})")









