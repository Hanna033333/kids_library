"""Supabase 데이터베이스 클라이언트"""
from supabase import create_client
from core.config import SUPABASE_URL, SUPABASE_KEY


# Supabase 클라이언트 초기화
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)



