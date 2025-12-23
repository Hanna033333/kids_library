#!/usr/bin/env python
"""
Apply migration to add curation_tag column to childbook_items
"""

from supabase_client import supabase
import os

def apply_migration():
    """curation_tag 컬럼 추가 migration 확인 및 안내"""
    
    print("🔧 Checking migration: Add curation_tag column to childbook_items...")
    
    try:
        # 테스트로 curation_tag 컬럼에 접근해보기
        result = supabase.table("childbook_items").select("curation_tag").limit(1).execute()
        print("✅ curation_tag 컬럼이 이미 존재합니다.")
        return True
    except Exception as e:
        error_msg = str(e)
        if "column" in error_msg.lower() and "curation_tag" in error_msg.lower():
            print("⚠️  curation_tag 컬럼이 존재하지 않습니다.")
            print("📝 Supabase 대시보드(SQL Editor)에서 다음 SQL을 실행해주세요:")
            
            migration_file = os.path.join(os.path.dirname(__file__), "migrations", "008_add_curation_tag_column.sql")
            print("\n" + "="*60)
            if os.path.exists(migration_file):
                with open(migration_file, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print("-- Add curation_tag column to childbook_items")
                print("ALTER TABLE childbook_items ADD COLUMN IF NOT EXISTS curation_tag TEXT;")
            print("="*60 + "\n")
            return False
        else:
            print(f"❌ 오류 발생: {e}")
            return False

if __name__ == "__main__":
    apply_migration()
