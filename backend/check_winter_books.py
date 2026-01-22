from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('../frontend/.env.local')

sb = create_client(os.getenv('NEXT_PUBLIC_SUPABASE_URL'), os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY'))

# Check winter books
res = sb.table('childbook_items').select('id, title, pangyo_callno, is_hidden').eq('curation_tag', '겨울방학2026').order('id').execute()

print(f'📚 Total winter books in DB: {len(res.data)}')

# Filter non-hidden books with callno
visible_with_callno = [b for b in res.data if (b.get('is_hidden') is None or b.get('is_hidden') == False) and b.get('pangyo_callno')]

print(f'✅ Visible books with callno: {len(visible_with_callno)}')
print(f'❌ Hidden or without callno: {len(res.data) - len(visible_with_callno)}')

print('\nFirst 10 visible books with callno:')
for i, book in enumerate(visible_with_callno[:10], 1):
    print(f'{i}. [{book["id"]}] {book["title"]} - {book.get("pangyo_callno")}')
