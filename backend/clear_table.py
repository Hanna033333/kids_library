from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ⚠ 테이블 전체 삭제
supabase.table("childbook_items").delete().neq("id", -1).execute()

print("childbook_items 전체 삭제 완료!")







