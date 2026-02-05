import os
import time
import requests
import concurrent.futures
from dotenv import load_dotenv
from core.database import supabase
from typing import List, Dict

# 환경변수 로딩 (보안: 하드코딩 제거)
load_dotenv()
ALADIN_TTBKEY = os.getenv("ALADIN_TTB_KEY")

if not ALADIN_TTBKEY:
    print("❌ Error: ALADIN_TTB_KEY not found in .env file")
    exit(1) 

def fetch_books_needing_images() -> List[Dict]:
    """Fetch books that have ISBN but no image_url"""
    # We fetch only items with valid ISBN
    print("Fetching books needing images...")
    
    # Remove isbn13 from select as it doesn't exist
    res = supabase.table("childbook_items") \
        .select("id, title, isbn") \
        .is_("image_url", "null") \
        .not_.is_("isbn", "null") \
        .execute()
        
    books = res.data
    
    print(f"Found {len(books)} books needing images.")
    return books

def fetch_aladin_image(isbn: str) -> str:
    """Fetch image URL from Aladin API"""
    url = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {
        "ttbkey": ALADIN_TTBKEY,
        "itemIdType": "ISBN13" if len(isbn) == 13 else "ISBN",
        "ItemId": isbn,
        "output": "js", # JSON
        "Version": "20131101",
        "Cover": "Big"
    }
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "item" in data and len(data["item"]) > 0:
                return data["item"][0].get("cover", "")
    except Exception as e:
        # print(f"Error fetching {isbn}: {e}")
        pass
        
    return ""

def process_book(book):
    isbn = book.get("isbn")
    if not isbn:
        isbn = book.get("isbn13")
        
    if not isbn:
        return None
        
    # Validation: strip hyphens just in case
    clean_isbn = isbn.replace("-", "").strip()
    if not clean_isbn:
        return None
        
    image_url = fetch_aladin_image(clean_isbn)
    
    if image_url:
        # Update DB
        try:
            supabase.table("childbook_items").update({"image_url": image_url}).eq("id", book["id"]).execute()
            return f"Updated {book['title']} -> {image_url}"
        except Exception as e:
            return f"Failed DB update {book['title']}: {e}"
    else:
        return f"No image found for {book['title']} ({clean_isbn})"

def main():
    books = fetch_books_needing_images()
    if not books:
        print("No item to process.")
        return

    print(f"Processing {len(books)} books with 10 threads...")
    
    success_count = 0
    fail_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_book, book) for book in books]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            if result:
                if "Updated" in result:
                    success_count += 1
                    print(f"[{i+1}/{len(books)}] {result}")
                else:
                    fail_count += 1
                    # print(f"[{i+1}/{len(books)}] {result}") # Reduce noise
            
            if i % 50 == 0:
                print(f"Progress: {i}/{len(books)}...")

    print(f"Done. Success: {success_count}, No Image/Fail: {fail_count}")

if __name__ == "__main__":
    main()
