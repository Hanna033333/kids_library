import csv
import json

# CSV 파일 읽기
csv_file = r'c:\Users\skplanet\Desktop\kids library\2025년 겨울방학 권장도서 목록 및 해제(서지사항 및 해제).csv'

books = []

try:
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        print("=== CSV 컬럼 ===")
        print(reader.fieldnames)
        print()
        
        print("=== 도서 목록 ===")
        for i, row in enumerate(reader, 1):
            books.append(row)
            print(f"{i}. {row}")
            print()
        
        print(f"\n총 {len(books)}권의 책이 있습니다.")
        
    # JSON으로 저장
    with open('winter_books_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    
    print("\n✅ winter_books_parsed.json 파일로 저장 완료!")
    
except Exception as e:
    print(f"❌ 에러: {e}")
    
    # 다른 인코딩 시도
    try:
        print("\n다른 인코딩(cp949)으로 재시도...")
        with open(csv_file, 'r', encoding='cp949') as f:
            reader = csv.DictReader(f)
            print("컬럼:", reader.fieldnames)
            for i, row in enumerate(reader, 1):
                books.append(row)
                print(f"{i}. {row}")
        
        with open('winter_books_parsed.json', 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        
        print("\n✅ winter_books_parsed.json 파일로 저장 완료!")
    except Exception as e2:
        print(f"❌ 재시도 실패: {e2}")
