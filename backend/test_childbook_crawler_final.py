from childbook_crawler import fetch_childbook_recommendations

print("어린이 도서 연구회 추천 도서 크롤링 테스트")
print("=" * 60)

books = fetch_childbook_recommendations(page=1)

print(f"\n수집된 도서 수: {len(books)}권\n")

if books:
    print("첫 3개 샘플:")
    for i, book in enumerate(books[:3], 1):
        print(f"\n{i}. {book['title']}")
        print(f"   지은이: {book['author']}")
        print(f"   출판사: {book['publisher']} | {book['year']} | {book['pages']}")
        print(f"   연령: {book['age']} | 갈래: {book['category']} | 가격: {book['price']}")
        print(f"   내용: {book['description'][:100]}...")








