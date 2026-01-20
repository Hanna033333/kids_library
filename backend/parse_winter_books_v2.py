import csv
import json

# CSV 파일 읽기 - 헤더 스킵하고 수동으로 파싱
csv_file = r'c:\Users\skplanet\Desktop\kids library\2025년 겨울방학 권장도서 목록 및 해제(서지사항 및 해제).csv'

books = []

try:
    with open(csv_file, 'r', encoding='cp949') as f:
        lines = f.readlines()
        
        print(f"총 {len(lines)}줄")
        print("\n=== 첫 10줄 ===")
        for i, line in enumerate(lines[:10], 1):
            print(f"{i}: {line.strip()}")
        
        # CSV 리더로 다시 읽기
        f.seek(0)
        reader = csv.reader(f)
        
        all_rows = list(reader)
        print(f"\n총 {len(all_rows)}행")
        
        # 헤더 찾기
        for i, row in enumerate(all_rows[:10]):
            print(f"Row {i}: {row}")
        
        # 실제 데이터 행 찾기 (보통 3-4행부터 시작)
        data_start = 0
        for i, row in enumerate(all_rows):
            if len(row) > 2 and row[0].isdigit():
                data_start = i
                print(f"\n데이터 시작 행: {data_start}")
                break
        
        # 헤더 추출 (데이터 시작 전 행에서)
        if data_start > 0:
            header_row = all_rows[data_start - 1]
            print(f"헤더: {header_row}")
            
            # 데이터 파싱
            for row in all_rows[data_start:]:
                if len(row) >= 2 and row[0].isdigit():
                    book = {}
                    for i, value in enumerate(row):
                        if i < len(header_row):
                            book[header_row[i]] = value
                        else:
                            book[f'column_{i}'] = value
                    books.append(book)
        
        print(f"\n=== 파싱된 책 목록 ({len(books)}권) ===")
        for i, book in enumerate(books[:3], 1):
            print(f"\n{i}. {book}")
        
        # JSON으로 저장
        with open('winter_books_clean.json', 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ winter_books_clean.json 파일로 저장 완료! (총 {len(books)}권)")
        
except Exception as e:
    print(f"❌ 에러: {e}")
    import traceback
    traceback.print_exc()
