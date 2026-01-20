import json
import csv

# JSON 파일 읽기
with open('winter_books_callno_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 실패한 책들만 필터링
failed_books = []
for result in data['results']:
    if result['status'] != 'success':
        failed_books.append(result)

print(f"청구기호를 찾지 못한 책: {len(failed_books)}권")
print()

# CSV 파일 생성
csv_file = 'winter_books_missing_callno.csv'

with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    
    # 헤더
    writer.writerow(['번호', '제목', '저자', '상태', '비고'])
    
    # 데이터
    for i, book in enumerate(failed_books, 1):
        status_text = {
            'not_found': '검색 결과 없음',
            'no_callno': '검색 결과 있으나 청구기호 없음',
            'error': '에러'
        }.get(book['status'], book['status'])
        
        writer.writerow([
            i,
            book['title'],
            book['author'],
            status_text,
            '2025년 신간 미등록 가능성'
        ])
        
        print(f"{i}. {book['title']} - {book['author']}")

print()
print(f"✅ {csv_file} 파일 생성 완료!")
print(f"   총 {len(failed_books)}권의 책 정보 포함")
