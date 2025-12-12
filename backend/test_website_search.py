"""
웹사이트 검색 함수 테스트
"""
from search_pangyo_website import search_callno_from_website

# 테스트 항목들
test_items = [
    {"isbn": "9788936442484", "title": "거짓말이 가득"},
    {"isbn": "9788963721910", "title": "두근두근 한국사 1-2"},
    {"isbn": "9788993143911", "title": "48pt로 읽는 아이"},
]

print("=" * 60)
print("웹사이트 검색 함수 테스트")
print("=" * 60)
print()

for item in test_items:
    print(f"검색: {item['title']} (ISBN: {item['isbn']})")
    callno = search_callno_from_website(item['isbn'], item['title'])
    if callno:
        print(f"  ✅ 찾음: {callno}")
    else:
        print(f"  ❌ 찾지 못함")
    print()

