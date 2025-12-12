"""
샘플 데이터로 네이버 API 검색 테스트
"""
from library_api import search_isbn

test_cases = [
    ("100만 번 산 고양이", "사노 요코"),
    ("7년 동안의 잠", "박완서"),
    ("검은 새", "이수지"),
]

print("=" * 60)
print("샘플 데이터 네이버 API 검색 테스트")
print("=" * 60)
print()

for title, author in test_cases:
    print(f"제목: {title}")
    print(f"저자: {author}")
    
    isbn, score = search_isbn(title, author)
    
    if isbn:
        print(f"✅ ISBN: {isbn} (유사도: {score})")
    else:
        print(f"❌ ISBN을 찾지 못함 (유사도: {score})")
    
    print("-" * 60)
    print()



