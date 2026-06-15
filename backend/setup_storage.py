import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import supabase

def setup_storage():
    bucket_name = "threads_assets"
    print(f"📦 Supabase Storage 버킷 설정 시작: '{bucket_name}'")
    
    try:
        # 1. 기존 버킷 목록 조회
        buckets = supabase.storage.list_buckets()
        bucket_exists = False
        for b in buckets:
            if b.name == bucket_name:
                bucket_exists = True
                print(f"✅ 버킷 '{bucket_name}'이(가) 이미 존재합니다. (Public 여부: {b.public})")
                break
                
        # 2. 버킷이 없으면 생성
        if not bucket_exists:
            print(f"🆕 버킷 '{bucket_name}' 생성 중...")
            res = supabase.storage.create_bucket(bucket_name, options={"public": True})
            print(f"🎉 버킷 생성 성공: {res}")
            
    except Exception as e:
        print(f"❌ Storage 설정 중 에러 발생: {e}")

if __name__ == "__main__":
    setup_storage()
