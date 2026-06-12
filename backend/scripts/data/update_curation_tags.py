from supabase_client import supabase
import time

def update_curation_tags():
    print("🚀 Starting bulk update of curation_tag...")
    
    # 1. Total count 확인
    count_res = supabase.table("childbook_items").select("id", count="exact").execute()
    total_count = count_res.count
    print(f"📚 Total books to check: {total_count}")
    
    # 2. Update in chunks
    chunk_size = 100
    processed = 0
    updated = 0
    
    # Init tag
    TARGET_TAG = '어린이도서연구회'
    
    try:
        # 먼저 이미 태그가 있는 건 제외할 수 있지만, 요구사항은 "지금까지... 데이터에... 달아줘"니까
        # 강제로 다 덮어쓰거나, 없는 것만 하거나. 
        # "모든 기존 책"이라고 했으므로, 없는 것만 업데이트하는 게 안전하고 효율적일 듯.
        # 하지만 혹시 모르니 그냥 전체를 대상으로 하되, 이미 있는 건 건너뛰는 로직으로.
        
        # We can simply update all where curation_tag is null
        # Or just update ALL to be sure.
        # Let's do: Update where curation_tag is NULL
        
        while processed < total_count:
            # 가져올 때 curation_tag가 NULL인 것만 가져오면 더 효율적
            # But supabase-py select with filter is easy.
            
            print(f"🔄 Processing chunk... ({processed}/{total_count})")
            
            # Fetch IDs where curation_tag is null
            # Note: limit is applied to the result set.
            res = supabase.table("childbook_items") \
                .select("id") \
                .is_("curation_tag", "null") \
                .limit(chunk_size) \
                .execute()
            
            books = res.data
            
            if not books:
                print("✨ No more books without curation_tag found.")
                break
                
            # Update these books
            ids_to_update = [b['id'] for b in books]
            
            # Bulk update is not strictly supported as "update many with same value depending on ID list" in one REST call easily 
            # without 'in' filter.
            # We can use .in_()
            
            update_res = supabase.table("childbook_items") \
                .update({"curation_tag": TARGET_TAG}) \
                .in_("id", ids_to_update) \
                .execute()
                
            count = len(update_res.data)
            updated += count
            processed += count # roughly
            
            print(f"   ✅ Updated {count} books.")
            
            time.sleep(0.1) # throttling
            
    except Exception as e:
        print(f"❌ Error during update: {e}")
        
    print(f"\n🎉 Update complete! Total updated: {updated}")

if __name__ == "__main__":
    update_curation_tags()
