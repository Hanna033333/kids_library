import csv
from datetime import datetime
from supabase_client import supabase

def backup_to_csv():
    """현재 데이터 전체 백업"""
    print("📦 현재 데이터 백업 중...")
    
    # 모든 데이터 조회
    res = supabase.table("childbook_items") \
        .select("*") \
        .execute()
    
    books = res.data
    
    # CSV 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_before_update_{timestamp}.csv"
    
    if books:
        keys = books[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(books)
    
    print(f"✅ 백업 완료: {filename}")
    print(f"   총 {len(books)}권 저장\n")
    return filename

if __name__ == "__main__":
    backup_to_csv()
