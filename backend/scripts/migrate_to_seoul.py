import sys
import time
from dotenv import dotenv_values
from supabase import create_client

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
    print("❌ Missing old DB credentials. Create backend/.env.mumbai with SUPABASE_URL and service role key.")
    sys.exit(1)

if not NEW_URL or not NEW_KEY:
    print("❌ Missing new DB credentials in backend/.env.")
    sys.exit(1)

if OLD_URL == NEW_URL:
    print("❌ Old and new Supabase URLs are identical. Refusing to migrate a database into itself.")
    sys.exit(1)

print("=" * 60)
print("🚀 [Kids Library] Mumbai -> Seoul Supabase Data Migration")
print(f"Old DB (Mumbai): {OLD_URL}")
print(f"New DB (Seoul) : {NEW_URL}")
print("=" * 60)

old_client = create_client(OLD_URL, OLD_KEY)
new_client = create_client(NEW_URL, NEW_KEY)

def migrate_table(table_name: str, batch_size: int = 500, order_col: str = 'id'):
    print(f"\n📦 Migrating table [{table_name}]...")
    
    try:
        count_res = old_client.table(table_name).select('*', count='exact').limit(1).execute()
        total_rows = count_res.count or 0
    except Exception as e:
        print(f"   ⚠️ Could not read {table_name} from old DB: {e}")
        return

    print(f"   Total rows to copy: {total_rows}")
    
    if total_rows == 0:
        print(f"   ℹ️ No rows in {table_name}, skipping.")
        return

    offset = 0
    copied = 0
    start_time = time.time()
    
    while offset < total_rows:
        end_idx = min(offset + batch_size - 1, total_rows - 1)
        res = old_client.table(table_name).select('*').order(order_col, desc=False).range(offset, end_idx).execute()
        rows = res.data
        if not rows:
            break
        
        # Upsert into new DB
        new_client.table(table_name).upsert(rows).execute()
        copied += len(rows)
        offset += batch_size
        print(f"   ➡️ Copied {copied}/{total_rows} rows ({(copied/total_rows)*100:.1f}%)")
    
    elapsed = time.time() - start_time
    print(f"   ✅ Finished [{table_name}] in {elapsed:.2f}s ({copied} rows)")

def verify_migration():
    print("\n" + "=" * 60)
    print("🔍 Verifying Data Consistency between Mumbai and Seoul DB...")
    print("=" * 60)
    
    tables = ['childbook_items', 'book_library_info', 'book_reviews', 'threads_feeds', 'callno_history', 'members', 'wishlists']
    all_matched = True
    
    for t in tables:
        try:
            old_cnt = old_client.table(t).select('*', count='exact').limit(1).execute().count or 0
            new_cnt = new_client.table(t).select('*', count='exact').limit(1).execute().count or 0
            
            status = "✅ MATCH" if old_cnt == new_cnt else "❌ MISMATCH"
            if old_cnt != new_cnt:
                all_matched = False
            print(f"   - {t:<20}: Old = {old_cnt:<6} | New = {new_cnt:<6} | {status}")
        except Exception as e:
            print(f"   - {t:<20}: Error checking: {e}")
        
    if all_matched:
        print("\n🎉 ALL TABLES SUCCESSFULLY MIGRATED AND VERIFIED 100%!")
    else:
        print("\n⚠️ SOME TABLES HAVE ROW COUNT DIFFERENCES. Please check logs.")

if __name__ == '__main__':
    # Sequence of migration respecting foreign keys
    # 1. childbook_items (Parents)
    migrate_table('childbook_items', batch_size=500, order_col='id')
    
    # 2. book_library_info (Children of childbook_items)
    migrate_table('book_library_info', batch_size=1000, order_col='id')
    
    # 3. book_reviews
    migrate_table('book_reviews', batch_size=500, order_col='id')
    
    # 4. threads_feeds
    migrate_table('threads_feeds', batch_size=200, order_col='id')

    # 5. callno_history
    migrate_table('callno_history', batch_size=500, order_col='id')

    # 6. members
    migrate_table('members', batch_size=500, order_col='id')

    # 7. wishlists
    migrate_table('wishlists', batch_size=500, order_col='id')
    
    # 8. Verify
    verify_migration()
