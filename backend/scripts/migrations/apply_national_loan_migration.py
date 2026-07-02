import os
from supabase_client import supabase

def apply_migration():
    migration_file = 'migrations/011_add_national_loan_count.sql'
    print(f"🚀 마이그레이션 파일 읽는 중: {migration_file}")
    
    if not os.path.exists(migration_file):
        print(f"❌ 에러: {migration_file} 파일이 존재하지 않습니다.")
        return
        
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
        
    print("📡 Supabase DDL 실행 요청 중...")
    try:
        # DDL을 한 번에 실행하기 위해 exec_sql RPC 호출
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ 마이그레이션 적용 성공!")
        print("  - childbook_items 테이블에 national_loan_count 컬럼 추가 완료")
        print("  - idx_childbook_national_loan 인덱스 생성 완료")
    except Exception as e:
        print(f"❌ 마이그레이션 적용 실패: {e}")

if __name__ == "__main__":
    apply_migration()
