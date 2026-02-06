import json
import os
from supabase_client import supabase

# Read API results
with open('caldecott_enriched.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

sql_lines = []
sql_lines.append("-- 칼데콧 수상작 중복 해결 및 데이터 병합")
sql_lines.append("-- 생성일: 2026-02-06")

print("Checking for conflicts...")

for result in results:
    if result.get('status') == 'success' and result.get('isbn'):
        # Target (the one we inserted recently)
        target_title = result.get('korean_title') or result['original_title']
        target_title_esc = target_title.replace("'", "''")
        
        # New correct ISBN
        new_isbn = result['isbn']
        new_image = result.get('cover', '')
        
        # Check if ISBN already exists
        res = supabase.table("childbook_items").select("*").eq("isbn", new_isbn).execute()
        existing_items = res.data
        
        if existing_items:
            # Conflict exists? Check if it's the same item or different
            existing = existing_items[0]
            existing_id = existing['id']
            existing_title = existing['title']
            existing_tags = existing.get('curation_tag') or ''
            
            # Normalize titles for comparison (remove spaces, etc if needed, but simple exact match first)
            if existing_title.replace(" ", "") == target_title.replace(" ", ""):
                 # It's likely the same item (or we are updating the item that already has this ISBN - which is fine, no unique error)
                 # Check if we assume target is found by title '눈보라' and existing is '눈보라'.
                 # If we run UPDATE ... WHERE title='눈보라' .. SET isbn=...
                 # It touches the matching row. If that row already has the ISBN, it's fine.
                 # So we generate an UPDATE statement.
                 
                sql = f"""-- 업데이트: '{target_title}' (이미 ISBN 보유, 이미지/태그 보완)
UPDATE childbook_items 
SET isbn = '{new_isbn}',
    image_url = '{new_image}'
WHERE title = '{target_title_esc}' 
  AND curation_tag LIKE '%caldecott%';"""
                sql_lines.append(sql)
                
            else:
                # Different title -> Real Conflict (Duplicate)
                print(f"CONFLICT: '{target_title}' tries to use ISBN {new_isbn}, but '{existing_title}' (ID {existing_id}) has it.")
                
                # 1. Update existing item (Add tag 'caldecott' if missing)
                if 'caldecott' not in existing_tags:
                    new_tags = f"{existing_tags}, caldecott" if existing_tags else "caldecott"
                    sql = f"""-- 병합: 기존 '{existing_title}'에 태그 추가
UPDATE childbook_items
SET curation_tag = '{new_tags}'
WHERE id = {existing_id};"""
                    sql_lines.append(sql)
                else:
                    sql_lines.append(f"-- 기존 '{existing_title}' (ID {existing_id})는 이미 caldecott 태그 보유")
                
                # 2. Delete the target item (the incorrect placeholder we made)
                sql = f"""-- 삭제: 잘못된 정보로 생성된 '{target_title}' 삭제
DELETE FROM childbook_items
WHERE title = '{target_title_esc}' AND curation_tag LIKE '%caldecott%';"""
                sql_lines.append(sql)
                sql_lines.append("")
            
        else:
            # No conflict, just regular update (as previously planned)
            # But wait, checking logic:
            # If I run UPDATE table SET isbn=NEW WHERE title=TARGET
            # It works if NEW is not taken.
            
            sql = f"""-- 업데이트: '{target_title}' 정보 보완
UPDATE childbook_items 
SET isbn = '{new_isbn}',
    image_url = '{new_image}'
WHERE title = '{target_title_esc}' 
  AND curation_tag LIKE '%caldecott%';"""
            sql_lines.append(sql)
            sql_lines.append("")

# Write SQL
with open('fix_caldecott_conflicts_v2.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))

print("✅ Generated fix_caldecott_conflicts_v2.sql")
