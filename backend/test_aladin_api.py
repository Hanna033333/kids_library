"""
알라딘 API 및 통합 검색 함수 테스트
"""
from library_api import search_isbn_aladin, search_isbn_combined, search_isbn

print("=" * 60)
print("알라딘 API 및 통합 검색 함수 테스트")
print("=" * 60)
print()

# 테스트 케이스
test_cases = [
    ("해리포터", "조앤 롤링"),
    ("세상을 바꾼 큰 걸음", "김성훈"),
    ("아무도 모르는 작은 나라", "사토 사토루"),
]

for title, author in test_cases:
    print(f"제목: {title}")
    print(f"저자: {author}")
    print()
    
    # 알라딘 API 테스트
    print("1. 알라딘 API:")
    aladin_isbn, aladin_score = search_isbn_aladin(title, author)
    print(f"   ISBN: {aladin_isbn}, 유사도: {aladin_score}")
    
    # 네이버 API 테스트
    print("2. 네이버 API:")
    naver_isbn, naver_score = search_isbn(title, author)
    print(f"   ISBN: {naver_isbn}, 유사도: {naver_score}")
    
    # 통합 검색 테스트
    print("3. 통합 검색 (알라딘 + 네이버):")
    combined_isbn, combined_score, source = search_isbn_combined(title, author)
    print(f"   ISBN: {combined_isbn}, 유사도: {combined_score}, 소스: {source}")
    
    print("-" * 60)
    print()


