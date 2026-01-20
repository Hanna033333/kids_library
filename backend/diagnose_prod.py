import requests
import time
import json

BASE_URL = "https://kids-library-7gj8.onrender.com"

def check_prod():
    print(f"Checking {BASE_URL}...")
    
    # 1. Search Winter Books
    print("\n1. Searching Winter Books...")
    start = time.time()
    try:
        res = requests.get(f"{BASE_URL}/api/books/list?category=겨울방학", timeout=10) # API endpoint might be different, try list first
        # Actually API is /api/books/list AND /api/books/search using 'curation' tag? 
        # Wait, the code uses query params.
        # Let's try to find a winter book via raw query if possible or just get ANY book
        
        # Try getting book ID 1 first (usually safe)
        res = requests.get(f"{BASE_URL}/api/books/1", timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Time: {time.time() - start:.2f}s")
        if res.status_code == 200:
            print("Book 1 Data:", json.dumps(res.json(), indent=2, ensure_ascii=False)[:500] + "...")
        else:
            print("Error:", res.text)
            
        # Try finding a winter book ID from the previous SQL fix
        # Let's search for "겨울방학" curation via API
        # Frontend uses: /books?curation=겨울방학
        # API: /api/books/search?q=... no, look at api/books.py
        # router.get("/list") -> search_books_service
        # search_books_service handles 'curation' param? Let's check search.py
        
    except Exception as e:
        print(f"Exception: {e}")

check_prod()
