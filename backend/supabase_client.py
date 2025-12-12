from supabase import create_client
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"

# .env 파일에서 직접 읽기 (dotenv 실패 대비)
env_vars = {}
if env_path.exists():
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    try:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value:
                            env_vars[key] = value
                    except Exception:
                        continue
    except Exception:
        pass

# dotenv 시도 (실패해도 env_vars에 있음)
try:
    load_dotenv(dotenv_path=env_path, override=True)
except Exception:
    pass

# 환경 변수 설정 (env_vars에서)
for key, value in env_vars.items():
    if key not in os.environ:
        try:
            os.environ[key] = value
        except Exception:
            pass

url = os.getenv("SUPABASE_URL") or env_vars.get("SUPABASE_URL")
# 서비스 키 우선 사용 (RLS 우회), 없으면 일반 키 사용
service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or env_vars.get("SUPABASE_SERVICE_KEY") or env_vars.get("SUPABASE_SERVICE_ROLE_KEY")
key = service_key or os.getenv("SUPABASE_KEY") or env_vars.get("SUPABASE_KEY")

supabase = create_client(url, key)
