"""
no_callno_items.csv에 pangyo_callno 컬럼을 추가하여
수동 입력용 CSV 파일 생성
"""
import csv

print("=" * 60)
print("수동 입력용 CSV 파일 생성")
print("=" * 60)
print()

# 기존 CSV 읽기
input_filename = "no_callno_items.csv"
output_filename = "no_callno_items_manual.csv"

print(f"입력 파일: {input_filename}")
print(f"출력 파일: {output_filename}")
print()

items = []
try:
    with open(input_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            items.append(row)
    
    print(f"총 {len(items):,}개 항목 로드됨")
except Exception as e:
    print(f"오류: {e}")
    exit(1)

# 수동 입력용 CSV 생성 (pangyo_callno 컬럼 추가)
fieldnames = ['id', 'isbn', 'title', 'author', 'publisher', 'pangyo_callno', 'pangyo_callno_manual']

with open(output_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for item in items:
        row = {
            'id': item.get('id', ''),
            'isbn': item.get('isbn', ''),
            'title': item.get('title', ''),
            'author': item.get('author', ''),
            'publisher': item.get('publisher', ''),
            'pangyo_callno': item.get('pangyo_callno', '없음'),
            'pangyo_callno_manual': ''  # 여기에 수동으로 입력
        }
        writer.writerow(row)

print(f"✅ 수동 입력용 CSV 파일 생성 완료: {output_filename}")
print()
print("사용 방법:")
print("1. Excel이나 텍스트 에디터로 파일 열기")
print("2. 'pangyo_callno_manual' 컬럼에 웹사이트에서 찾은 청구기호 입력")
print("3. 입력 완료 후 update_from_manual_csv.py 실행")
print("=" * 60)

