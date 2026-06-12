# -*- coding: utf-8 -*-
import json
import csv
import sys
import io

# Set encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("📂 Loading data...")
    
    # 1. Load Original Targets
    with open('winter_books_clean.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
    print(f"  - Loaded {len(targets)} target books")

    # 2. Load Crawling Results
    results_map = {}
    try:
        with open('crawling_results.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    results_map[data['title']] = data
                except: pass
        print(f"  - Loaded {len(results_map)} crawling results")
    except FileNotFoundError:
        print("  - No crawling_results.jsonl found!")
        return

    # 3. Merge and Export
    output_file = 'winter_crawling_verification.csv'
    
    headers = ['연번', '서명', '저자', '발행자', '크롤링 상태', '매칭 타입', '청구기호', '에러 메시지']
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for book in targets:
            title = book['서명']
            result = results_map.get(title, {})
            
            row = [
                book.get('연번', ''),
                title,
                book.get('저자', ''),
                book.get('발행자', ''),
                result.get('status', 'not_run'),
                result.get('match_type', '-'),
                result.get('callno', '-'),
                result.get('error', '-')
            ]
            writer.writerow(row)
            
    print(f"\n✅ Export completed: {output_file}")

if __name__ == "__main__":
    main()
