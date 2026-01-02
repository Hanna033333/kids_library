#!/usr/bin/env python
"""
web_scraped_callno 컬럼 추가 마이그레이션
"""

from supabase_client import supabase


def add_web_scraped_callno_column():
    """
    childbook_items 테이블에 web_scraped_callno 컬럼 추가
    """
    print("\n" + "="*80)
    print("🔧 web_scraped_callno 컬럼 추가")
    print("="*80 + "\n")
    
    # Supabase에서는 Python 클라이언트로 직접 컬럼을 추가할 수 없으므로
    # SQL을 실행해야 합니다.
    
    sql = """
    ALTER TABLE childbook_items 
    ADD COLUMN IF NOT EXISTS web_scraped_callno TEXT;
    """
    
    try:
        # Supabase RPC를 통해 SQL 실행
        # 참고: 이 방법은 Supabase에서 SQL 함수를 미리 만들어야 합니다.
        print("📝 SQL 실행:")
        print(sql)
        print("\n⚠️  Supabase Python 클라이언트로는 직접 ALTER TABLE을 실행할 수 없습니다.")
        print("📌 다음 방법 중 하나를 선택하세요:\n")
        print("1. Supabase 대시보드 SQL Editor에서 직접 실행:")
        print("   https://supabase.com/dashboard/project/YOUR_PROJECT/sql\n")
        print("2. 또는 아래 명령을 복사하여 SQL Editor에 붙여넣기:")
        print("-"*80)
        print(sql)
        print("-"*80)
        
        # 컬럼이 이미 있는지 확인
        print("\n🔍 컬럼 존재 여부 확인 중...")
        try:
            response = supabase.table("childbook_items").select("web_scraped_callno").limit(1).execute()
            print("✅ web_scraped_callno 컬럼이 이미 존재합니다!")
            return True
        except Exception as e:
            print(f"❌ 컬럼이 아직 없습니다: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


if __name__ == "__main__":
    add_web_scraped_callno_column()
    
    print("\n" + "="*80)
    print("✅ 완료")
    print("="*80 + "\n")
