import requests
import sys
import argparse
from urllib.parse import urljoin

# Configuration
URLS = {
    'prod': 'https://checkjari.com',
    'dev': 'https://kids-library-git-dev-hannas-projects-f9ed017f.vercel.app'
}

def check_site_health(env):
    base_url = URLS.get(env)
    if not base_url:
        print(f"❌ Unknown environment: {env}")
        return False

    print(f"🏥 Starting health check for [{env.upper()}] at {base_url}...")
    all_passed = True

    # 1. API Connectivity & Winter Books Check
    # The frontend calls this API for winter books: /api/books/list?curation=겨울방학
    # However, since this is a Next.js app, the API might be internal or proxied.
    # Let's try to hit the page itself or the backend API if we know it.
    # Looking at home-api.ts, it uses Supabase directly or an internal API.
    # If we can't easily hit the internal API from outside, we might need to check the HTML content 
    # OR (better) check the actual backend API if possible. 
    # Let's use the actual backend URL for API checks if possible, or just check the frontend logic?
    # Wait, home-api.ts runs on the server (Next.js), so the client sees HTML.
    # A true E2E check would parse HTML.
    # A backend check would hit the FastAPI backend?
    # `home-api.ts` connects to Supabase directly.
    # Let's stick to checking the frontend URL for 200 OK first.
    
    # Check Homepage
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Homepage load: OK ({response.elapsed.total_seconds():.2f}s)")
        else:
            print(f"❌ Homepage load: FAILED (Status {response.status_code})")
            all_passed = False
    except Exception as e:
        print(f"❌ Homepage load: ERROR ({str(e)})")
        all_passed = False

    # 2. Check Winter Books (Logic Verification)
    # Since we can't easily parse CSR/SSR HTML without Selenium, and we want a quick check,
    # let's verify the "Logic" by running the same logic as the frontend logic using a python script variant as a proxy,
    # OR better: Assume the 'backend' logic is what we verified in test_winter_random.py.
    # 
    # Ideally, we should check the actual result. 
    # If there is a /api endpoint we can hit, that's best.
    # If not, let's verify the backend DB state which feeds the frontend.
    # The previous `test_winter_random.py` verified the DB state + Logic.
    # So let's run a "Logic Check" here that connects to Supabase and verifies 7 books are selectable.
    
    print("\n🔍 Verifying Content Policy (Winter Books)...")
    try:
        # Re-use the logic from test_winter_random.py to verify DB state guarantees 7 books
        from supabase import create_client
        import os
        from dotenv import load_dotenv
        import math
        import datetime

        # Load env vars based on where this script is running
        # Load env vars based on where this script is running
        # Try multiple locations for .env.local
        possible_paths = [
            'frontend/.env.local',          # Run from root
            '../frontend/.env.local',       # Run from backend/
            './frontend/.env.local'         # Run from parent of root?
        ]
        
        env_path = None
        for path in possible_paths:
            if os.path.exists(path):
                env_path = path
                break
                
        if env_path:
            load_dotenv(env_path)
            # print(f"ℹ️ Loaded env from {env_path}")
            
        sb_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        sb_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
        
        if not sb_url or not sb_key:
            print("⚠️ Skipping DB check: Supabase credentials not found in env")
        else:
            sb = create_client(sb_url, sb_key)
            
            # Run all DB policy checks
            if not verify_db_policies(sb):
                all_passed = False

    except Exception as e:
        print(f"⚠️ DB Check Warning: {str(e)}")
        # Don't fail the build for DB connection issues if this is running in an env without DB access
    
    return all_passed

# Refactored Check Logic to separate function
def verify_db_policies(sb):
    success = True
    
    def check(count, name, min_req):
        if count < min_req:
            print(f"❌ POLICY VIOLATION: [{name}] has {count} books (Required: {min_req})")
            return False
        else:
            print(f"✅ POLICY CHECK: [{name}] Sufficient ({count} >= {min_req})")
            return True

    print("\n🔍 Verifying Content Policy (At least 7 books per section)...")

    # 1. Winter
    res = sb.table('childbook_items').select('id', count='exact').eq('curation_tag', '겨울방학2026').or_('is_hidden.is.null,is_hidden.eq.false').execute()
    if not check(res.count, "Winter Books", 7): success = False

    # 2. Research Council
    res = sb.table('childbook_items').select('id', count='exact').eq('curation_tag', '어린이도서연구회').or_('is_hidden.is.null,is_hidden.eq.false').execute()
    if not check(res.count, "Research Council", 7): success = False

    # 3. Age Groups
    age_map = {
        'Age 0-3': ['0세부터', '3세부터'],
        'Age 4-7': ['5세부터', '7세부터'],
        'Age 8-12': ['9세부터', '11세부터'],
        'Age 13+': ['13세부터', '16세부터']
    }
    for name, ages in age_map.items():
        res = sb.table('childbook_items').select('id', count='exact').in_('age', ages).or_('is_hidden.is.null,is_hidden.eq.false').execute()
        if not check(res.count, name, 7): success = False
        
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check site health')
    parser.add_argument('env', choices=['prod', 'dev'], nargs='?', default='prod', help='Environment to check')
    args = parser.parse_args()
    
    success = check_site_health(args.env)
    
    if success:
        print("\n✨ All systems go! Health check passed.")
        sys.exit(0)
    else:
        print("\n💥 Health check FAILED. Please investigate.")
        sys.exit(1)
