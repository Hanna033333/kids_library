import os
import sys

# Add current directory to path to allow imports
sys.path.append(os.getcwd())

from core.database import supabase
from collections import Counter

def analyze_duplicates():
    print("청구기호 중복 분석 시작...")
    
    # 1. Fetch all call numbers (using pagination if needed, but for now assuming reasonable size or adjusting limit)
    # Supabase default limit is 1000. Let's try to fetch more or paginate if strictly needed.
    # For a quick analysis, let's fetch a large chunk.
    
    all_books = []
    page = 0
    limit = 1000
    
    while True:
        start = page * limit
        end = start + limit - 1
        
        response = supabase.table("childbook_items") \
            .select("title, pangyo_callno") \
            .range(start, end) \
            .execute()
            
        if not response.data:
            break
            
        all_books.extend(response.data)
        
        if len(response.data) < limit:
            break
            
        page += 1
        print(f"{len(all_books)}권 데이터 로드 중...")

    print(f"총 {len(all_books)}권의 데이터를 분석합니다.")

    # 2. Count call numbers
    call_counts = Counter()
    call_to_titles = {} # To store titles for each call number
    
    for book in all_books:
        callno = book.get("pangyo_callno")
        title = book.get("title")
        
        if not callno:
            continue
            
        call_counts[callno] += 1
        
        if callno not in call_to_titles:
            call_to_titles[callno] = []
        call_to_titles[callno].append(title)

    # 3. Filter duplicates
    duplicates = {k: v for k, v in call_counts.items() if v > 1}
    
    # 4. Report to file
    with open("analysis_result.txt", "w", encoding="utf-8") as f:
        f.write("\n=== 분석 결과 ===\n")
        f.write(f"중복된 청구기호 종류: {len(duplicates)}개\n")
        
        total_duplicate_books = sum(duplicates.values())
        f.write(f"중복된 청구기호를 가진 총 책 수: {total_duplicate_books}권\n")
        
        if not duplicates:
            f.write("중복된 청구기호가 없습니다.\n")
            return

        f.write("\n[가장 많이 중복된 청구기호 TOP 20]\n")
        sorted_dupes = sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:20]
        
        for callno, count in sorted_dupes:
            f.write(f"\n청구기호: {callno} ({count}권)\n")
            titles = call_to_titles[callno][:3]
            titles_str = ", ".join(titles)
            if len(call_to_titles[callno]) > 3:
                titles_str += "..."
            f.write(f" - 포함된 책들: {titles_str}\n")
    
    print("분석 완료! analysis_result.txt 파일을 확인하세요.")

if __name__ == "__main__":
    try:
        analyze_duplicates()
    except Exception as e:
        print(f"오류 발생: {e}")
