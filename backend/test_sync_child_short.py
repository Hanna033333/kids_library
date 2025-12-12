from crawler import fetch_library_books_child

# 짧은 기간으로 테스트 (최근 1개월)
books = fetch_library_books_child('2024-12-01', '2024-12-31')
print(f'수집된 아동 도서: {len(books)}권')
if books:
    print(f'\n첫 5개 샘플:')
    for i, book in enumerate(books[:5], 1):
        print(f"{i}. {book['title']} - {book['author']} (분류번호: {book['kdc']})")
else:
    print('아동 도서 없음')









