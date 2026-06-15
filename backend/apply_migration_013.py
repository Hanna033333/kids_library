import os
import sys

# Ensure backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import supabase

def apply_migration():
    migration_file = 'migrations/013_add_scheduling_columns_to_threads_feeds.sql'
    print(f"🚀 마이그레이션 파일 읽는 중: {migration_file}")
    
    if not os.path.exists(migration_file):
        print(f"❌ 에러: {migration_file} 파일이 존재하지 않습니다.")
        return
        
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
        
    print("📡 Supabase DDL 실행 요청 중...")
    try:
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ 마이그레이션 013 적용 성공!")
        print("  - threads_feeds 테이블에 curation_tag 및 scheduled_at 컬럼 추가 완료")
        print("  - public SELECT RLS 정책 적용 완료")
    except Exception as e:
        print(f"❌ 마이그레이션 적용 실패: {e}")

if __name__ == "__main__":
    apply_migration()
