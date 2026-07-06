import os

def get_ga_key_path() -> str:
    """
    GOOGLE_APPLICATION_CREDENTIALS 환경변수가 명시되어 있으면 우선적으로 해당 경로를 반환하고,
    그렇지 않으면 기존 로컬 파일 경로인 backend/ga4-key.json 으로 폴백합니다.
    """
    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path:
        return env_path
        
    # 기존 로컬 폴백 경로 설정 (scripts/analysis 위치를 기준으로 상위 backend 디렉토리 아래)
    base_dir = os.path.dirname(os.path.abspath(__file__)) # .../backend/scripts/analysis
    backend_dir = os.path.dirname(base_dir) # .../backend
    local_fallback = os.path.join(backend_dir, "ga4-key.json")
    return local_fallback
