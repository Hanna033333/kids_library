"""
총서 번호 가져오기 함수 테스트
"""
from crawler import get_series_number_from_website

print("=" * 60)
print("총서 번호 가져오기 함수 테스트")
print("=" * 60)
print()

# '밤마다 환상축제' 책의 ISBN과 제목
isbn = "9788901238678"
title = "밤마다 환상축제"

print(f"ISBN: {isbn}")
print(f"제목: {title}")
print("웹사이트에서 총서 번호 가져오는 중...")
print()

series_number = get_series_number_from_website(isbn, title)

if series_number:
    print(f"✅ 총서 번호 찾음: {series_number}")
else:
    print("❌ 총서 번호를 찾을 수 없습니다.")

