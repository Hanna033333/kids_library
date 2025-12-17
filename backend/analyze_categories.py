import csv
from supabase_client import supabase
from collections import Counter

def analyze_categories():
    print("데이터 조회 중...")
    
    categories = []
    chunk_size = 1000
    start = 0
    while True:
        response = supabase.table("childbook_items").select("category").range(start, start + chunk_size - 1).execute()
        chunk = response.data
        if not chunk:
            break
        categories.extend([item.get("category") for item in chunk])
        if len(chunk) < chunk_size:
            break
        start += chunk_size
        
    print(f"총 도서 수: {len(categories)}권")
    
    # 빈 값 처리 ("" 또는 None -> "미분류")
    cleaned_cats = [c if c and c.strip() else "미분류" for c in categories]
    
    counts = Counter(cleaned_cats)
    
    print(f"\n[카테고리 현황 (총 {len(counts)}개 종류)]")
    # 개수 많은 순 정렬
    sorted_cats = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    for cat, count in sorted_cats:
        print(f"{cat}: {count}권")

if __name__ == "__main__":
    analyze_categories()
