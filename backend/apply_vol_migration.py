#!/usr/bin/env python
"""
Apply migration to add vol column to childbook_items
"""

from supabase_client import supabase

def apply_migration():
    """vol 컬럼 추가 migration 적용"""
    
    print("🔧 Applying migration: Add vol column to childbook_items...")
    
    # SQL 직접 실행 (Supabase는 RPC를 통해 실행)
    # 대신 Python으로 컬럼 존재 여부 확인 후 추가
    
    try:
        # 테스트로 vol 컬럼에 접근해보기
        result = supabase.table("childbook_items").select("vol").limit(1).execute()
        print("✅ vol 컬럼이 이미 존재합니다.")
        return True
    except Exception as e:
        error_msg = str(e)
        if "column" in error_msg.lower() and "vol" in error_msg.lower():
            print("⚠️  vol 컬럼이 존재하지 않습니다.")
            print("📝 Supabase 대시보드에서 다음 SQL을 실행해주세요:")
            print("\n" + "="*60)
            with open("migrations/007_add_vol_column.sql", "r", encoding="utf-8") as f:
                print(f.read())
            print("="*60 + "\n")
            return False
        else:
            print(f"❌ 오류 발생: {e}")
            return False

if __name__ == "__main__":
    apply_migration()
