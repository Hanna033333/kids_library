import csv
import os
import sys
import time
from crawler import get_series_number_from_website

# Add current directory to path
sys.path.append(os.getcwd())

def fix_duplicates():
    input_file = "check_duplicates_cleaned.csv"
    output_sql = "migrations/002_fix_duplicate_callnumbers.sql"
    
    print(f"Reading {input_file}...")
    
    books_to_fix = []
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            books_to_fix.append(row)
            
    print(f"Total {len(books_to_fix)} books to process.")
    
    fixed_count = 0
    failed_count = 0
    
    with open(output_sql, 'w', encoding='utf-8') as sql_file:
        sql_file.write("-- Fix duplicate call numbers by adding volume numbers\n")
        sql_file.write("BEGIN;\n\n")
        
        # Thread-safe writing
        import threading
        file_lock = threading.Lock()
        
        def process_book(book):
            nonlocal fixed_count, failed_count
            isbn = book['ISBN']
            title = book['제목']
            current_callno = book['청구기호']
            book_id = book['ID']
            
            try:
                # print(f"Processing: {title}...", end="", flush=True)
                series_no = get_series_number_from_website(isbn, title, current_callno)
                
                if series_no:
                    new_callno = f"{current_callno}-{series_no}"
                    with file_lock:
                        print(f"[FIXED] {title}: {series_no} -> {new_callno}")
                        sql = f"UPDATE childbook_items SET pangyo_callno = '{new_callno}' WHERE id = {book_id};\n"
                        sql_file.write(sql)
                        fixed_count += 1
                else:
                    # with file_lock:
                    #     print(f"[FAIL] {title}: Not found")
                    pass
            except Exception as e:
                print(f"Error processing {title}: {e}")

        from concurrent.futures import ThreadPoolExecutor
        
        # Update concurrently with 10 workers
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(process_book, books_to_fix))
            
        sql_file.write("\nCOMMIT;\n")
    
    # Calculate failed count correctly
    failed_count = len(books_to_fix) - fixed_count

    print("\n=== Summary ===")
    print(f"Total Processed: {len(books_to_fix)}")
    print(f"Fixed: {fixed_count}")
    print(f"Failed: {failed_count}")
    print(f"SQL file generated: {output_sql}")

if __name__ == "__main__":
    fix_duplicates()
