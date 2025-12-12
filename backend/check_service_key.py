"""
서비스 키 사용 여부 확인
"""
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
regular_key = os.getenv("SUPABASE_KEY")

print("=" * 60)
print("Supabase 키 확인")
print("=" * 60)
print()

print(f"SUPABASE_URL: {'설정됨' if url else '없음'}")
print(f"SUPABASE_SERVICE_KEY: {'설정됨' if service_key else '없음'}")
print(f"SUPABASE_SERVICE_ROLE_KEY: {'설정됨' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else '없음'}")
print(f"SUPABASE_KEY: {'설정됨' if regular_key else '없음'}")
print()

if service_key:
    print("✅ 서비스 키가 설정되어 있습니다. RLS를 우회할 수 있습니다.")
    print(f"사용할 키: {'SUPABASE_SERVICE_KEY' if os.getenv('SUPABASE_SERVICE_KEY') else 'SUPABASE_SERVICE_ROLE_KEY'}")
else:
    print("⚠️ 서비스 키가 설정되어 있지 않습니다.")
    print("RLS 정책 때문에 library_items 테이블에 저장할 수 없을 수 있습니다.")
    print()
    print("해결 방법:")
    print("1. Supabase 대시보드에서 Service Role Key를 복사")
    print("2. .env 파일에 SUPABASE_SERVICE_KEY 또는 SUPABASE_SERVICE_ROLE_KEY 추가")







