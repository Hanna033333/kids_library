from services.search import search_books_service
import asyncio

def test_filters():
    print("Testing Category Filter...")
    
    # 1. Test Category='동화'
    res = search_books_service(category="동화", limit=5)
    print(f"Category '동화' count: {len(res['data'])}")
    for book in res['data']:
        if book['category'] != '동화':
            print(f"❌ Error: Found category {book['category']} in '동화' filter")
        else:
            print(f"✅ OK: {book['title']} ({book['category']})")

    # 2. Test Category='과학'
    res_sci = search_books_service(category="과학", limit=5)
    print(f"\nCategory '과학' count: {len(res_sci['data'])}")
    for book in res_sci['data']:
        print(f"✅ OK: {book['title']} ({book['category']})")

if __name__ == "__main__":
    test_filters()
