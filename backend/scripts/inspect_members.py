import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('/Users/1004823/Desktop/kids_library/backend/.env')

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(url, key)

try:
    # members 테이블의 임의의 레코드 하나를 가져와 컬럼을 확인
    res = supabase.table("members").select("*").limit(1).execute()
    print("Members Data Example:", res.data)
except Exception as e:
    print("Error:", e)
