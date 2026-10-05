import sys
import urllib3
urllib3.disable_warnings()

from supabase import create_client
from dotenv import dotenv_values

# 1. Configs
old_env = dotenv_values('backend/.env.mumbai')
new_env = dotenv_values('backend/.env')

OLD_URL = old_env.get('SUPABASE_URL')
OLD_KEY = (
    old_env.get('SUPABASE_SERVICE_KEY')
    or old_env.get('SUPABASE_SERVICE_ROLE_KEY')
    or old_env.get('SUPABASE_KEY')
)

NEW_URL = new_env.get('SUPABASE_URL')
NEW_KEY = (
    new_env.get('SUPABASE_SERVICE_KEY')
    or new_env.get('SUPABASE_SERVICE_ROLE_KEY')
    or new_env.get('SUPABASE_KEY')
)

if not OLD_URL or not OLD_KEY:
    print("❌ Missing old DB credentials. Ensure backend/.env.mumbai has SUPABASE_URL and service role key.")
    sys.exit(1)

if not NEW_URL or not NEW_KEY:
    print("❌ Missing new DB credentials in backend/.env.")
    sys.exit(1)

if OLD_URL == NEW_URL:
    print("❌ Old and new Supabase URLs are identical.")
    sys.exit(1)

print("=" * 65)
print("🚀 [Kids Library] Auth Users, Members & Wishlists Migration to Seoul")
print(f"Old DB (Mumbai): {OLD_URL}")
print(f"New DB (Seoul) : {NEW_URL}")
print("=" * 65)

old_client = create_client(OLD_URL, OLD_KEY)
new_client = create_client(NEW_URL, NEW_KEY)

def migrate_auth_and_members():
    # 1. Fetch old auth users
    print("\n1️⃣ Fetching auth.users from Mumbai DB...")
    old_users = old_client.auth.admin.list_users()
    print(f"   Found {len(old_users)} auth users in Mumbai DB.")

    # 2. Check new auth users
    new_users = new_client.auth.admin.list_users()
    new_user_ids = {u.id for u in new_users}
    print(f"   Currently {len(new_users)} auth users in Seoul DB.")

    # 3. Create missing auth users in Seoul DB
    print("\n2️⃣ Migrating auth.users to Seoul DB...")
    for u in old_users:
        if u.id in new_user_ids:
            print(f"   ⏭️ User already exists in Seoul: {u.id} ({u.email})")
            continue
        try:
            attrs = {
                'id': u.id,
                'email': u.email,
                'email_confirm': True,
                'user_metadata': u.user_metadata or {},
                'app_metadata': u.app_metadata or {},
            }
            new_client.auth.admin.create_user(attrs)
            print(f"   ✅ Created user in Seoul: {u.id} ({u.email}) [Provider: {u.app_metadata.get('provider') if u.app_metadata else 'unknown'}]")
        except Exception as e:
            print(f"   ❌ Error creating user {u.id} ({u.email}): {e}")

    # 4. Fetch and migrate members
    print("\n3️⃣ Migrating public.members data...")
    old_members = old_client.table('members').select('*').order('created_at').execute().data
    print(f"   Found {len(old_members)} members in Mumbai DB.")
    
    if old_members:
        for m in old_members:
            try:
                new_client.table('members').upsert(m).execute()
                print(f"   ✅ Upserted member: {m['id']} | {m['email']} | {m['nickname']} | {m['provider']}")
            except Exception as e:
                print(f"   ❌ Error upserting member {m['id']}: {e}")

    # 5. Fetch and migrate wishlists
    print("\n4️⃣ Migrating public.wishlists data...")
    old_wishlists = old_client.table('wishlists').select('*').order('id').execute().data
    print(f"   Found {len(old_wishlists)} wishlists in Mumbai DB.")
    
    if old_wishlists:
        for w in old_wishlists:
            try:
                new_client.table('wishlists').upsert(w).execute()
                print(f"   ✅ Upserted wishlist item: ID={w['id']} | User={w['user_id']} | Book={w['book_id']}")
            except Exception as e:
                print(f"   ❌ Error upserting wishlist {w['id']}: {e}")

    # 6. Verify migration
    print("\n" + "=" * 65)
    print("🔍 [Verification] Comparing Mumbai vs Seoul DB Data Counts")
    print("=" * 65)

    final_old_users = old_client.auth.admin.list_users()
    final_new_users = new_client.auth.admin.list_users()
    print(f" - auth.users       : Mumbai = {len(final_old_users):<4} | Seoul = {len(final_new_users):<4} | {'✅ MATCH' if len(final_old_users) == len(final_new_users) else '❌ MISMATCH'}")

    final_old_m = old_client.table('members').select('*', count='exact').limit(1).execute().count or 0
    final_new_m = new_client.table('members').select('*', count='exact').limit(1).execute().count or 0
    print(f" - public.members   : Mumbai = {final_old_m:<4} | Seoul = {final_new_m:<4} | {'✅ MATCH' if final_old_m == final_new_m else '❌ MISMATCH'}")

    final_old_w = old_client.table('wishlists').select('*', count='exact').limit(1).execute().count or 0
    final_new_w = new_client.table('wishlists').select('*', count='exact').limit(1).execute().count or 0
    print(f" - public.wishlists : Mumbai = {final_old_w:<4} | Seoul = {final_new_w:<4} | {'✅ MATCH' if final_old_w == final_new_w else '❌ MISMATCH'}")

    print("=" * 65)

if __name__ == '__main__':
    migrate_auth_and_members()
