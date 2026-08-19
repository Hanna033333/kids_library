import os
import sys

# Ensure backend root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database import supabase

def apply_migration():
    sql = """
    ALTER TABLE book_reviews ADD COLUMN IF NOT EXISTS nickname TEXT;
    ALTER TABLE book_reviews ADD COLUMN IF NOT EXISTS child_age TEXT;
    ALTER TABLE book_reviews ADD COLUMN IF NOT EXISTS rating NUMERIC(2,1);
    ALTER TABLE book_reviews ADD COLUMN IF NOT EXISTS selected_badges TEXT[] DEFAULT '{}';
    ALTER TABLE book_reviews ADD COLUMN IF NOT EXISTS content TEXT;
    ALTER TABLE book_reviews ADD COLUMN IF NOT EXISTS is_ai_generated BOOLEAN DEFAULT FALSE;
    """
    print("📡 Supabase DDL 실행 요청 중 (015_create_book_reviews)...")
    try:
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ 마이그레이션 적용 성공!", result)
    except Exception as e:
        print(f"❌ exec_sql RPC 실패 ({e}), direct query 시도...")
        # RPC가 없거나 실패할 경우 개별 SQL 실행
        try:
            with open('migrations/015_create_book_reviews.sql', 'r', encoding='utf-8') as f:
                full_sql = f.read()
            supabase.rpc('exec_sql', {'sql': full_sql}).execute()
            print("✅ 015_create_book_reviews.sql 적용 성공!")
        except Exception as e2:
            print(f"❌ 마이그레이션 2차 실행 실패: {e2}")

if __name__ == "__main__":
    apply_migration()
