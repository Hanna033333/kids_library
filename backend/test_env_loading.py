"""
환경 변수 로딩 테스트
"""
import os
import sys

# recategorize_winter_safe.py의 load_env_manual 함수 복사
def load_env_manual():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    paths_to_check = [
        os.path.join(current_dir, ".env"),
        os.path.join(os.path.dirname(current_dir), ".env"),
    ]
    
    env_vars = {}
    for path in paths_to_check:
        print(f"체크: {path}")
        if os.path.exists(path):
            print(f"  ✅ 존재함")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"): continue
                        if "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip().strip("'").strip('"')
                print(f"  ✅ 로드 성공: {len(env_vars)} 개 변수")
                break
            except Exception as e:
                print(f"  ❌ 로드 실패: {e}")
        else:
            print(f"  ❌ 없음")
    return env_vars

env = load_env_manual()

print(f"\n로드된 환경 변수:")
print(f"  SUPABASE_URL: {env.get('SUPABASE_URL', 'NOT FOUND')[:50]}...")
print(f"  SUPABASE_KEY: {env.get('SUPABASE_KEY', 'NOT FOUND')[:50]}...")
print(f"  GEMINI_API_KEY: {env.get('GEMINI_API_KEY', 'NOT FOUND')[:50]}...")

# supabase_client.py와 비교
from supabase_client import supabase
print(f"\nsupabase_client.py의 Supabase URL:")
print(f"  {supabase.supabase_url[:50]}...")
