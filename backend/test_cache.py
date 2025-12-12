import sys
if 'crawler' in sys.modules:
    del sys.modules['crawler']

from crawler import PANGYO_CODE
print(f'도서관 코드: {PANGYO_CODE}')

from crawler import fetch_library_books_child
books = fetch_library_books_child('2024-01-01', '2024-12-31')
print(f'수집된 아동 도서: {len(books)}권')
if books:
    print('첫 3개:', books[:3])










