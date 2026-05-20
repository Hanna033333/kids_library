"""
데이터베이스 내 칼데콧 수상작들의 curation_tag를 안전하게 복원하는 스크립트.
기존의 AI 태그(#태그)를 보존하면서 뒤에 ',caldecott' 형태로 덧붙여서 복원합니다.
"""
import json
import os
import sys
from core.database import supabase

def restore_caldecott_tags():
    print("🚀 Starting Caldecott curation_tag restoration...")
    
    # 1. caldecott_final.json 로드
    json_path = "caldecott_final.json"
    if not os.path.exists(json_path):
        json_path = os.path.join(os.path.dirname(__file__), "caldecott_final.json")
        
    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} file not found!")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        caldecott_books = json.load(f)
        
    print(f"📚 Loaded {len(caldecott_books)} books from caldecott_final.json")
    
    success_count = 0
    skipped_count = 0
    not_found_count = 0
    
    # 2. 각 책 순회하며 복원 진행
    for idx, cb in enumerate(caldecott_books, 1):
        isbn = cb.get("isbn")
        korean_title = cb.get("korean_title")
        original_title = cb.get("original_title")
        
        target_title = korean_title or original_title
        print(f"\n[{idx}/{len(caldecott_books)}] Processing: '{target_title}'")
        
        matched_book = None
        
        # A. ISBN으로 먼저 매칭 시도
        if isbn:
            res = supabase.table("childbook_items") \
                .select("id, title, curation_tag, is_hidden, isbn") \
                .eq("isbn", isbn) \
                .execute()
            if res.data:
                matched_book = res.data[0]
                print(f"   -> Matched by ISBN: '{matched_book['title']}' (ID: {matched_book['id']})")
                
        # B. ISBN 매칭이 실패한 경우 제목으로 시도
        if not matched_book and target_title:
            res = supabase.table("childbook_items") \
                .select("id, title, curation_tag, is_hidden, isbn") \
                .eq("title", target_title) \
                .execute()
            if res.data:
                matched_book = res.data[0]
                print(f"   -> Matched by Title: '{matched_book['title']}' (ID: {matched_book['id']})")
                
        # C. 매칭된 책이 있는 경우 복원 처리
        if matched_book:
            current_tags = matched_book.get("curation_tag") or ""
            new_tags = ""
            
            # 태그 분석 및 합성
            if not current_tags:
                new_tags = "caldecott"
            else:
                tag_list = [t.strip() for t in current_tags.split(",") if t.strip()]
                if "caldecott" in tag_list:
                    print(f"   -> Already has 'caldecott' tag. Skipping database update.")
                    skipped_count += 1
                    continue
                else:
                    tag_list.append("caldecott")
                    new_tags = ",".join(tag_list)
            
            # DB 업데이트 실행
            try:
                update_res = supabase.table("childbook_items") \
                    .update({"curation_tag": new_tags}) \
                    .eq("id", matched_book["id"]) \
                    .execute()
                    
                if update_res.data:
                    print(f"   ✅ DB updated successfully! Tags: '{current_tags}' -> '{new_tags}'")
                    success_count += 1
                else:
                    print(f"   ❌ DB update returned empty data for ID: {matched_book['id']}")
            except Exception as e:
                print(f"   ❌ Error updating DB for ID {matched_book['id']}: {e}")
        else:
            print(f"   ⚠️ Could not find this book in childbook_items (ISBN: {isbn}, Title: '{target_title}')")
            not_found_count += 1
            
    # 최종 리포트 출력
    print("\n" + "=" * 50)
    print("🎉 Caldecott Restoration Summary")
    print(f"- Total processed: {len(caldecott_books)}")
    print(f"- Successfully updated: {success_count}")
    print(f"- Already up to date: {skipped_count}")
    print(f"- Not found in DB: {not_found_count}")
    print("=" * 50)

if __name__ == "__main__":
    restore_caldecott_tags()
