from crawler import fetch_library_books_child
import sys

# 디버깅을 위해 print 출력 확인
books = fetch_library_books_child('2024-01-01', '2024-12-31')
print(f'\n최종 결과: {len(books)}권')
if books:
    print('첫 3개:', books[:3])










