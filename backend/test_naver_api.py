"""
네이버 API 테스트
"""
from library_api import search_isbn

# 테스트 케이스
test_cases = [
    ("해리포터와 마법사의 돌", "J.K. 롤링"),
    ("토끼와 거북이", None),
    ("백설공주", None),
]

print("=" * 60)
print("네이버 API 테스트")
print("=" * 60)
print()

for title, author in test_cases:
    print(f"제목: {title}")
    if author:
        print(f"저자: {author}")
    print()
    
    isbn, score = search_isbn(title, author)
    
    if isbn:
        print(f"✅ ISBN: {isbn} (유사도: {score})")
    else:
        print(f"❌ ISBN을 찾지 못함 (유사도: {score})")
    
    print("-" * 60)
    print()



