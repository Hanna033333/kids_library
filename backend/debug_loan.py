import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def run():
    # 1. Get 20 books
    print("Fetching 20 books...")
    try:
        r = requests.get(f"{BASE_URL}/api/books/list?limit=20")
        data = r.json()
        books = data['books']
    except Exception as e:
        print(f"Failed to fetch books: {e}")
        return

    book_ids = [b['id'] for b in books]
    print(f"Fetched {len(book_ids)} books.")

    # 2. Check loan status
    print("Checking loan status...")
    try:
        r = requests.post(f"{BASE_URL}/api/books/loan-status", json=book_ids)
        statuses = r.json()
        
        # Stats
        total = len(statuses)
        available = sum(1 for s in statuses.values() if s.get('available') is True)
        unavailable = sum(1 for s in statuses.values() if s.get('available') is False)
        unknown = sum(1 for s in statuses.values() if s.get('available') is None)
        
        print("-" * 30)
        print(f"Total Checked: {total}")
        print(f"Available (Green): {available}")
        print(f"Unavailable (Red): {unavailable}")
        print(f"Unknown (Gray): {unknown}")
        print("-" * 30)
        
        # Print samples of Unknown
        if unknown > 0:
            print("Sample Unknowns:")
            count = 0
            for bid, s in statuses.items():
                if s.get('available') is None:
                    print(f"Book {bid}: {s}")
                    count += 1
                    if count >= 3: break

    except Exception as e:
        print(f"Failed to check loan: {e}")

if __name__ == "__main__":
    run()
