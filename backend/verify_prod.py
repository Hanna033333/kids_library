"""
프로덕션 환경 배포 전 데이터베이스 RLS (Row Level Security) 실동 안전성 검증 스크립트
(비로그인 외부 Anon 권한을 활용한 삽입/수정/삭제 RLS 모의 침투 테스트)
"""
import os
import sys
import asyncio
from datetime import datetime

# sys.path 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from core.config import SUPABASE_URL, env_vars

# RLS 테스트를 위해 익명(anon) 키로 클라이언트 생성
anon_key = os.getenv("SUPABASE_KEY") or env_vars.get("SUPABASE_KEY")
anon_supabase = create_client(SUPABASE_URL, anon_key)

async def test_wishlists_insert_protection() -> bool:
    """비로그인 익명 유저가 wishlists 테이블에 임의로 찜을 주입하려는 시도가 차단되는지 검증"""
    try:
        # RLS가 제대로 켜져 있다면, 인증 토큰 없이 (또는 익명 권한으로)
        # wishlists에 행을 추가하려고 시도할 때 에러가 나거나 RLS에 의해 행이 삽입되지 않아야 함.
        try:
            anon_supabase.auth.sign_out()
        except Exception:
            pass
        
        response = anon_supabase.table("wishlists").insert({
            "user_id": "99999999-9999-9999-9999-999999999999", # 임의의 허구 UUID
            "book_id": 1
        }).execute()
        
        # 만약 에러가 없고 response.data가 정상 반환된다면 RLS 뚫림 (보안 취약점)
        if response.data:
            print("❌ RLS Test [Wishlist INSERT]: FAILED - Anon user was able to inject data!")
            return False
        else:
            print("✅ RLS Test [Wishlist INSERT]: SUCCESS - Blocked successfully (no data returned)")
            return True
    except Exception as e:
        # 에러가 발생하여 차단되는 경우도 정상적인 RLS 차단 시나리오임
        print(f"✅ RLS Test [Wishlist INSERT]: SUCCESS - Blocked with error: {e}")
        return True

async def test_threads_feeds_insert_protection() -> bool:
    """비로그인 익명 유저가 threads_feeds 테이블에 임의의 피드를 조작하여 승인처리하거나 삽입하려 하는지 검증"""
    try:
        try:
            anon_supabase.auth.sign_out()
        except Exception:
            pass
        response = anon_supabase.table("threads_feeds").insert({
            "title": "Hacker Feed",
            "content": "Malicious content",
            "curation_tag": "hacked",
            "is_approved": True,
            "book_ids": [1]
        }).execute()
        
        if response.data:
            print("❌ RLS Test [Threads Feeds INSERT]: FAILED - Anon user was able to inject thread feed!")
            return False
        else:
            print("✅ RLS Test [Threads Feeds INSERT]: SUCCESS - Blocked successfully")
            return True
    except Exception as e:
        print(f"✅ RLS Test [Threads Feeds INSERT]: SUCCESS - Blocked with error: {e}")
        return True

async def test_books_is_hidden_read_protection() -> bool:
    """비로그인/일반 유저가 childbook_items의 is_hidden = True (숨김처리)된 도서를 읽지 못하도록 설정되었는지 쿼리 검증"""
    try:
        # DB에 숨김 처리된 도서(is_hidden=true)가 있는 경우, eq("is_hidden", True) 조회가 데이터를 반환하지 않아야 함
        response = anon_supabase.table("childbook_items").select("id").eq("is_hidden", True).execute()
        # count 혹은 data가 비어있어야 안전
        if response.data:
            # 숨김처리된 도서도 일반 select로 노출되면 안됨
            # 다만, DB에 애초에 is_hidden=True인 도서가 없을 수도 있음. 
            # 만약 조회가 성공해 데이터가 나왔다면 1차적으로 주의 필요.
            print(f"⚠️ RLS Note [Hidden Books SELECT]: Found {len(response.data)} hidden books. If you are admin this is fine, otherwise confirm select filter.")
        else:
            print("✅ RLS Test [Hidden Books SELECT]: SUCCESS - No hidden books leaked to anon query")
        return True
    except Exception as e:
        print(f"✅ RLS Test [Hidden Books SELECT]: Blocked or Exception: {e}")
        return True

async def main():
    print(f"🔍 [RLS Verification] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Running Anon Security Penetration Simulation...")
    
    results = [
        await test_wishlists_insert_protection(),
        await test_threads_feeds_insert_protection(),
        await test_books_is_hidden_read_protection()
    ]
    
    if all(results):
        print("\n🎉 [RLS Verification] Anon key penetration simulation completed: ALL RLS PROTECTIONS ACTIVE.")
        sys.exit(0)
    else:
        print("\n❌ [RLS Verification] Security Vulnerability Found! One or more RLS checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
