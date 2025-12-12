"""환경 변수 관리 모듈"""
import os
from pathlib import Path
from dotenv import load_dotenv


def load_env_vars():
    """환경 변수 로딩 (dotenv + 직접 파일 읽기)"""
    env_path = Path(__file__).parent.parent / ".env"
    
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
    
    # dotenv 시도
    try:
        load_dotenv(dotenv_path=env_path, override=True)
    except Exception:
        pass
    
    # 환경 변수 설정
    for key, value in env_vars.items():
        if key not in os.environ:
            try:
                os.environ[key] = value
            except Exception:
                pass
    
    return env_vars


# 환경 변수 로딩
env_vars = load_env_vars()


# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL") or env_vars.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY") 
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY") 
    or env_vars.get("SUPABASE_SERVICE_KEY") 
    or env_vars.get("SUPABASE_SERVICE_ROLE_KEY")
)
SUPABASE_KEY = SUPABASE_SERVICE_KEY or os.getenv("SUPABASE_KEY") or env_vars.get("SUPABASE_KEY")


# API 키
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID") or env_vars.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET") or env_vars.get("NAVER_CLIENT_SECRET")
DATA4LIBRARY_KEY = os.getenv("DATA4LIBRARY_KEY") or env_vars.get("DATA4LIBRARY_KEY")
ALADIN_TTB_KEY = os.getenv("ALADIN_TTB_KEY") or env_vars.get("ALADIN_TTB_KEY")

