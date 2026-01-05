from supabase_client import supabase
import csv

def update_remaining_callnos():
    """완전히 다른 청구기호도 모두 업데이트"""
    print("📚 나머지 청구기호 업데이트 중...\n")
    
    # CSV에서 ID 목록 읽기
    different_ids = []
    with open('different_callnos_20260105_130332.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            different_ids.append(int(row['id']))
    
    print(f"업데이트 대상: {len(different_ids)}권\n")
    
    # 각 ID에 대해 업데이트
    updated = 0
    for book_id in different_ids:
        # 해당 책의 web_scraped_callno로 pangyo_callno 업데이트
        res = supabase.table("childbook_items") \
            .select("web_scraped_callno") \
            .eq("id", book_id) \
            .execute()
        
        if res.data:
            scraped = res.data[0]['web_scraped_callno']
            
            supabase.table("childbook_items") \
                .update({"pangyo_callno": scraped}) \
                .eq("id", book_id) \
                .execute()
            
            updated += 1
            
            if updated % 50 == 0:
                print(f"   진행 중: {updated}권...")
    
    print(f"\n✅ 업데이트 완료: {updated}권")
    print(f"   총 업데이트: 300+ + {updated} = {300 + updated}권 이상\n")

if __name__ == "__main__":
    update_remaining_callnos()
